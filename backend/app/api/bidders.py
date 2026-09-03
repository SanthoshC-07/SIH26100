import os
import re
import uuid
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models.models import (
    Bidder, Tender, Document, DocumentPage, ExtractedEntity,
    ComplianceCheck, ComplianceScore, RiskAssessment, Recommendation,
    OfficerReview, User, BidderProject, BidderPersonnel
)
from app.schemas.schemas import (
    BidderCreate, BidderResponse, BidderDetailResponse,
    DocumentResponse, ComplianceCheckResponse, ComplianceScoreResponse,
    RiskAssessmentResponse, RecommendationResponse,
    BidderProjectCreate, BidderProjectResponse,
    BidderPersonnelCreate, BidderPersonnelResponse
)
from app.api.deps import get_current_user
from app.documents.extractor import DocumentExtractor
from app.documents.entity_extractor import EntityExtractor
from app.services.compliance_engine import ComplianceEngine
from app.audit.audit_service import AuditService
from app.core.logging_config import logger

router = APIRouter(prefix="/bidders", tags=["Bidders"])

def validate_pan_format_raw(pan: Optional[str]) -> Optional[str]:
    if not pan:
        return None
    pan_clean = pan.strip().upper()
    if not pan_clean:
        return None
    if not re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", pan_clean):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "BIDDER_VALIDATION_ERROR",
                "message": f"PAN format '{pan_clean}' is invalid. Expected format: 5 letters, 4 digits, 1 letter (e.g. BSZPP1234K).",
                "field": "pan"
            }
        )
    return pan_clean

def validate_gstin_format_raw(gstin: Optional[str]) -> Optional[str]:
    if not gstin:
        return None
    gstin_clean = gstin.strip().upper()
    if not gstin_clean:
        return None
    if not re.match(r"^[0-9]{2}[A-Z0-9]{10}[A-Z0-9]{1}[Z]{1}[A-Z0-9]{1}$", gstin_clean):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "BIDDER_VALIDATION_ERROR",
                "message": f"GSTIN format '{gstin_clean}' is invalid. Expected 15-character statutory format (e.g. 29MOCKP1234M1Z5).",
                "field": "gstin"
            }
        )
    return gstin_clean

def process_and_save_document(
    db: Session,
    bidder: Bidder,
    file: UploadFile,
    document_type: str,
    user_id: Optional[str]
) -> Document:
    original_filename = file.filename or "bidder_document.pdf"
    file_ext = os.path.splitext(original_filename)[1].lower()

    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_FILE_TYPE",
                "message": f"Invalid file extension '{file_ext}'. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}",
                "field": "file"
            }
        )

    safe_filename = f"bidder_{bidder.id}_{uuid.uuid4().hex[:8]}{file_ext}"
    dest_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(dest_path)

    # Decoupled text and OCR extraction (never fail bidder creation on extraction error)
    extracted = {
        "full_text": "",
        "pages": [{"page_number": 1, "text": "", "has_tables": False, "ocr_applied": False, "confidence": 1.0}],
        "page_count": 1,
        "is_scanned": False,
        "extraction_method": "PDF_TEXT"
    }
    try:
        extracted = DocumentExtractor.extract_text_and_tables(dest_path)
    except Exception as e:
        logger.warning(f"Decoupled OCR/Text extraction warning for {dest_path}: {e}")

    doc = Document(
        bidder_id=bidder.id,
        tender_id=bidder.tender_id,
        document_name=original_filename,
        original_filename=original_filename,
        document_type=document_type,
        file_path=dest_path,
        file_size=file_size,
        mime_type=file.content_type or "application/pdf",
        is_scanned=extracted.get("is_scanned", False),
        extraction_method=extracted.get("extraction_method", "PDF_TEXT"),
        page_count=extracted.get("page_count", 1),
        extracted_text=extracted.get("full_text", ""),
        uploaded_by=user_id
    )
    db.add(doc)
    db.flush()

    # Save document pages
    for p in extracted.get("pages", []):
        d_page = DocumentPage(
            document_id=doc.id,
            page_number=p.get("page_number", 1),
            page_text=p.get("text", ""),
            has_tables=p.get("has_tables", False),
            ocr_applied=p.get("ocr_applied", False),
            extraction_method=extracted.get("extraction_method", "PDF_TEXT"),
            confidence=p.get("confidence", 1.0)
        )
        db.add(d_page)

    # Extract entities safely
    try:
        entities = EntityExtractor.extract_all(extracted.get("full_text", ""), extracted.get("pages", []))
        for ent in entities:
            db_ent = ExtractedEntity(
                document_id=doc.id,
                entity_type=ent["entity_type"],
                entity_value=ent["entity_value"],
                normalized_value=ent.get("normalized_value"),
                confidence=ent["confidence"],
                page_number=ent.get("page_number", 1),
                context_snippet=ent.get("context_snippet")
            )
            db.add(db_ent)
    except Exception as e:
        logger.warning(f"Entity extraction skipped on document {doc.id}: {e}")

    db.commit()
    db.refresh(doc)
    return doc

# ----------------- LIST BIDDERS -----------------
@router.get("", response_model=List[BidderResponse])
def list_bidders(tender_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Bidder)
    if tender_id:
        query = query.filter(Bidder.tender_id == tender_id)
    bidders = query.order_by(Bidder.created_at.desc()).all()
    
    results = []
    for b in bidders:
        score_val = b.compliance_score.overall_score if b.compliance_score else None
        risk_val = b.risk_assessment.risk_level if b.risk_assessment else None
        rec_val = b.recommendation.recommendation_type if b.recommendation else None
        
        results.append({
            "id": b.id,
            "tender_id": b.tender_id,
            "legal_name": b.legal_name,
            "trade_name": b.trade_name,
            "bidder_name": b.legal_name,
            "gstin": b.gstin,
            "pan": b.pan,
            "registered_address": b.registered_address,
            "contact_information": b.contact_information,
            "bidder_type": b.bidder_type,
            "country": b.country,
            "oil_gas_experience_years": b.oil_gas_experience_years,
            "pipeline_experience_years": b.pipeline_experience_years,
            "udyam_number": b.udyam_number,
            "cin": b.cin,
            "email": b.email,
            "phone": b.phone,
            "contact_person": b.contact_person,
            "status": b.status,
            "submitted_at": b.submitted_at,
            "created_at": b.created_at,
            "compliance_score": score_val,
            "risk_level": risk_val,
            "recommendation_type": rec_val,
            "documents_count": len(b.documents)
        })
    return results

# ----------------- CREATE BIDDER (JSON) -----------------
@router.post("", response_model=BidderResponse)
def create_bidder(
    bidder_in: BidderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tender = db.query(Tender).filter(Tender.id == bidder_in.tender_id).first()
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TENDER_NOT_FOUND", "message": "The specified pipeline tender was not found.", "field": "tender_id"}
        )

    resolved_name = (bidder_in.legal_name or bidder_in.bidder_name or "").strip()
    if not resolved_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "REQUIRED_FIELD_MISSING", "message": "Company / Legal Name is required.", "field": "legal_name"}
        )

    validated_pan = validate_pan_format_raw(bidder_in.pan)
    validated_gstin = validate_gstin_format_raw(bidder_in.gstin)

    # Check for duplicate PAN within the same tender
    if validated_pan:
        existing_pan = db.query(Bidder).filter(Bidder.tender_id == tender.id, Bidder.pan == validated_pan).first()
        if existing_pan:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "BIDDER_ALREADY_EXISTS", "message": f"A bidder with PAN '{validated_pan}' already exists in this tender.", "field": "pan"}
            )

    # Check for duplicate Legal Name within the same tender
    existing_name = db.query(Bidder).filter(Bidder.tender_id == tender.id, Bidder.legal_name.ilike(resolved_name)).first()
    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "BIDDER_ALREADY_EXISTS", "message": f"A bidder with legal name '{resolved_name}' is already registered in this tender.", "field": "legal_name"}
        )

    bidder = Bidder(
        tender_id=bidder_in.tender_id,
        legal_name=resolved_name,
        trade_name=bidder_in.trade_name,
        gstin=validated_gstin,
        pan=validated_pan,
        registered_address=bidder_in.registered_address,
        contact_information=bidder_in.contact_information or {},
        bidder_type=bidder_in.bidder_type or "INDIAN_EPC_CONTRACTOR",
        country=bidder_in.country or "INDIA",
        oil_gas_experience_years=bidder_in.oil_gas_experience_years or 0.0,
        pipeline_experience_years=bidder_in.pipeline_experience_years or 0.0,
        udyam_number=bidder_in.udyam_number,
        cin=bidder_in.cin,
        email=bidder_in.email,
        phone=bidder_in.phone,
        contact_person=bidder_in.contact_person,
        status="SUBMITTED"
    )
    db.add(bidder)
    db.commit()
    db.refresh(bidder)

    AuditService.log_action(
        db=db,
        action="BIDDER_CREATED",
        entity_type="BIDDER",
        entity_id=bidder.id,
        user_id=current_user.id,
        user_name=current_user.name,
        tender_id=tender.id,
        bidder_id=bidder.id,
        new_state={"legal_name": bidder.legal_name, "gstin": bidder.gstin, "pan": bidder.pan},
        reason=f"Created bidder {bidder.legal_name} for pipeline tender {tender.tender_number}"
    )

    return {
        "id": bidder.id,
        "tender_id": bidder.tender_id,
        "legal_name": bidder.legal_name,
        "trade_name": bidder.trade_name,
        "bidder_name": bidder.legal_name,
        "gstin": bidder.gstin,
        "pan": bidder.pan,
        "registered_address": bidder.registered_address,
        "contact_information": bidder.contact_information,
        "bidder_type": bidder.bidder_type,
        "country": bidder.country,
        "oil_gas_experience_years": bidder.oil_gas_experience_years,
        "pipeline_experience_years": bidder.pipeline_experience_years,
        "udyam_number": bidder.udyam_number,
        "cin": bidder.cin,
        "email": bidder.email,
        "phone": bidder.phone,
        "contact_person": bidder.contact_person,
        "status": bidder.status,
        "submitted_at": bidder.submitted_at,
        "created_at": bidder.created_at,
        "compliance_score": None,
        "risk_level": None,
        "recommendation_type": None,
        "documents_count": 0
    }

# ----------------- CREATE BIDDER WITH DOCUMENTS (MULTIPART FORMDATA) -----------------
@router.post("/with-documents", response_model=BidderResponse)
async def create_bidder_with_documents(
    tender_id: str = Form(...),
    legal_name: str = Form(...),
    trade_name: Optional[str] = Form(None),
    pan: Optional[str] = Form(None),
    gstin: Optional[str] = Form(None),
    documents: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TENDER_NOT_FOUND", "message": "The specified pipeline tender was not found.", "field": "tender_id"}
        )

    resolved_name = legal_name.strip()
    if not resolved_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "REQUIRED_FIELD_MISSING", "message": "Company / Legal Name is required.", "field": "legal_name"}
        )

    validated_pan = validate_pan_format_raw(pan)
    validated_gstin = validate_gstin_format_raw(gstin)

    if validated_pan:
        existing_pan = db.query(Bidder).filter(Bidder.tender_id == tender.id, Bidder.pan == validated_pan).first()
        if existing_pan:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "BIDDER_ALREADY_EXISTS", "message": f"A bidder with PAN '{validated_pan}' already exists in this tender.", "field": "pan"}
            )

    existing_name = db.query(Bidder).filter(Bidder.tender_id == tender.id, Bidder.legal_name.ilike(resolved_name)).first()
    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "BIDDER_ALREADY_EXISTS", "message": f"A bidder with legal name '{resolved_name}' is already registered in this tender.", "field": "legal_name"}
        )

    bidder = Bidder(
        tender_id=tender_id,
        legal_name=resolved_name,
        trade_name=trade_name,
        gstin=validated_gstin,
        pan=validated_pan,
        bidder_type="INDIAN_EPC_CONTRACTOR",
        country="INDIA",
        status="SUBMITTED"
    )
    db.add(bidder)
    db.commit()
    db.refresh(bidder)

    # Process and save any attached files
    saved_docs = []
    if documents:
        for f in documents:
            if f.filename:
                d = process_and_save_document(db, bidder, f, "BIDDER_SUBMISSION", current_user.id)
                saved_docs.append(d)

    # Auto-run compliance verification safely
    if saved_docs:
        try:
            ComplianceEngine.run_full_verification(
                db=db,
                bidder_id=bidder.id,
                officer_id=current_user.id,
                officer_name=current_user.name
            )
        except Exception as e:
            logger.warning(f"Auto-verification warning on bidder {bidder.id}: {e}")

    AuditService.log_action(
        db=db,
        action="BIDDER_CREATED",
        entity_type="BIDDER",
        entity_id=bidder.id,
        user_id=current_user.id,
        user_name=current_user.name,
        tender_id=tender.id,
        bidder_id=bidder.id,
        new_state={"legal_name": bidder.legal_name, "pan": bidder.pan, "documents_uploaded": len(saved_docs)},
        reason=f"Created bidder {bidder.legal_name} with {len(saved_docs)} dossier documents"
    )

    db.refresh(bidder)
    score_val = bidder.compliance_score.overall_score if bidder.compliance_score else None
    risk_val = bidder.risk_assessment.risk_level if bidder.risk_assessment else None
    rec_val = bidder.recommendation.recommendation_type if bidder.recommendation else None

    return {
        "id": bidder.id,
        "tender_id": bidder.tender_id,
        "legal_name": bidder.legal_name,
        "trade_name": bidder.trade_name,
        "bidder_name": bidder.legal_name,
        "gstin": bidder.gstin,
        "pan": bidder.pan,
        "registered_address": bidder.registered_address,
        "contact_information": bidder.contact_information,
        "bidder_type": bidder.bidder_type,
        "country": bidder.country,
        "oil_gas_experience_years": bidder.oil_gas_experience_years,
        "pipeline_experience_years": bidder.pipeline_experience_years,
        "udyam_number": bidder.udyam_number,
        "cin": bidder.cin,
        "email": bidder.email,
        "phone": bidder.phone,
        "contact_person": bidder.contact_person,
        "status": bidder.status,
        "submitted_at": bidder.submitted_at,
        "created_at": bidder.created_at,
        "compliance_score": score_val,
        "risk_level": risk_val,
        "recommendation_type": rec_val,
        "documents_count": len(bidder.documents)
    }

# ----------------- GET BIDDER DETAIL -----------------
@router.get("/{id}", response_model=BidderDetailResponse)
def get_bidder(id: str, db: Session = Depends(get_db)):
    bidder = db.query(Bidder).filter(Bidder.id == id).first()
    if not bidder:
        raise HTTPException(status_code=404, detail="Bidder not found")

    score_val = bidder.compliance_score.overall_score if bidder.compliance_score else None
    risk_val = bidder.risk_assessment.risk_level if bidder.risk_assessment else None
    rec_val = bidder.recommendation.recommendation_type if bidder.recommendation else None

    projects = db.query(BidderProject).filter(BidderProject.bidder_id == id).all()
    personnel = db.query(BidderPersonnel).filter(BidderPersonnel.bidder_id == id).all()

    return {
        "id": bidder.id,
        "tender_id": bidder.tender_id,
        "legal_name": bidder.legal_name,
        "trade_name": bidder.trade_name,
        "bidder_name": bidder.legal_name,
        "gstin": bidder.gstin,
        "pan": bidder.pan,
        "registered_address": bidder.registered_address,
        "contact_information": bidder.contact_information,
        "bidder_type": bidder.bidder_type,
        "country": bidder.country,
        "oil_gas_experience_years": bidder.oil_gas_experience_years,
        "pipeline_experience_years": bidder.pipeline_experience_years,
        "udyam_number": bidder.udyam_number,
        "cin": bidder.cin,
        "email": bidder.email,
        "phone": bidder.phone,
        "contact_person": bidder.contact_person,
        "status": bidder.status,
        "submitted_at": bidder.submitted_at,
        "created_at": bidder.created_at,
        "compliance_score": score_val,
        "risk_level": risk_val,
        "recommendation_type": rec_val,
        "documents_count": len(bidder.documents),
        "documents": bidder.documents,
        "projects": projects,
        "personnel": personnel,
        "compliance_checks": bidder.compliance_checks,
        "compliance_score_detail": bidder.compliance_score,
        "risk_assessment_detail": bidder.risk_assessment,
        "recommendation_detail": bidder.recommendation,
        "officer_reviews": bidder.officer_reviews
    }

# ----------------- UPLOAD DOCUMENTS TO EXISTING BIDDER -----------------
@router.post("/{id}/documents", response_model=DocumentResponse)
async def upload_bidder_document(
    id: str,
    file: UploadFile = File(...),
    document_type: str = Form("GENERAL"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bidder = db.query(Bidder).filter(Bidder.id == id).first()
    if not bidder:
        raise HTTPException(status_code=404, detail="Bidder not found")

    doc = process_and_save_document(db, bidder, file, document_type, current_user.id)

    # Auto-run compliance verification
    try:
        ComplianceEngine.run_full_verification(
            db=db,
            bidder_id=bidder.id,
            officer_id=current_user.id,
            officer_name=current_user.name
        )
    except Exception as e:
        logger.warning(f"Post-upload verification trigger warning: {e}")

    return {
        "id": doc.id,
        "bidder_id": doc.bidder_id,
        "tender_id": doc.tender_id,
        "document_name": doc.document_name,
        "original_filename": doc.original_filename,
        "document_type": doc.document_type,
        "file_size": doc.file_size,
        "mime_type": doc.mime_type,
        "is_scanned": doc.is_scanned,
        "page_count": doc.page_count,
        "upload_timestamp": doc.upload_timestamp,
        "entities_count": len(doc.entities)
    }

# ----------------- BIDDER PROJECTS SUB-ROUTES -----------------
@router.get("/{id}/projects", response_model=List[BidderProjectResponse])
def list_bidder_projects(id: str, db: Session = Depends(get_db)):
    bidder = db.query(Bidder).filter(Bidder.id == id).first()
    if not bidder:
        raise HTTPException(status_code=404, detail="Bidder not found")
    return db.query(BidderProject).filter(BidderProject.bidder_id == id).all()

@router.post("/{id}/projects", response_model=BidderProjectResponse)
def add_bidder_project(
    id: str,
    project_in: BidderProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bidder = db.query(Bidder).filter(Bidder.id == id).first()
    if not bidder:
        raise HTTPException(status_code=404, detail="Bidder not found")

    project = BidderProject(
        bidder_id=id,
        project_name=project_in.project_name,
        client_name=project_in.client_name,
        client_type=project_in.client_type or "PUBLIC_SECTOR_UNDERTAKING",
        sector=project_in.sector or "OIL_AND_GAS",
        project_type=project_in.project_type or "PIPELINE_CONSTRUCTION",
        pipeline_type=project_in.pipeline_type or "NATURAL_GAS",
        pipeline_length_km=project_in.pipeline_length_km,
        pipeline_diameter=project_in.pipeline_diameter,
        project_value=project_in.project_value or 0.0,
        currency=project_in.currency or "INR",
        location=project_in.location,
        start_date=project_in.start_date,
        completion_date=project_in.completion_date,
        scope_of_work=project_in.scope_of_work,
        bidder_role=project_in.bidder_role or "EPC_CONTRACTOR",
        contract_reference=project_in.contract_reference,
        evidence_document_id=project_in.evidence_document_id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

# ----------------- BIDDER PERSONNEL SUB-ROUTES -----------------
@router.get("/{id}/personnel", response_model=List[BidderPersonnelResponse])
def list_bidder_personnel(id: str, db: Session = Depends(get_db)):
    bidder = db.query(Bidder).filter(Bidder.id == id).first()
    if not bidder:
        raise HTTPException(status_code=404, detail="Bidder not found")
    return db.query(BidderPersonnel).filter(BidderPersonnel.bidder_id == id).all()

@router.post("/{id}/personnel", response_model=BidderPersonnelResponse)
def add_bidder_personnel(
    id: str,
    personnel_in: BidderPersonnelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bidder = db.query(Bidder).filter(Bidder.id == id).first()
    if not bidder:
        raise HTTPException(status_code=404, detail="Bidder not found")

    personnel = BidderPersonnel(
        bidder_id=id,
        name=personnel_in.name,
        designation=personnel_in.designation,
        qualification=personnel_in.qualification,
        specialization=personnel_in.specialization,
        years_of_experience=personnel_in.years_of_experience,
        oil_gas_experience_years=personnel_in.oil_gas_experience_years,
        pipeline_experience_years=personnel_in.pipeline_experience_years,
        certifications=personnel_in.certifications or [],
        relevant_projects=personnel_in.relevant_projects or [],
        document_id=personnel_in.document_id
    )
    db.add(personnel)
    db.commit()
    db.refresh(personnel)
    return personnel

# ----------------- VERIFICATION TRIGGER -----------------
@router.post("/{id}/verify")
def verify_bidder(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bidder = db.query(Bidder).filter(Bidder.id == id).first()
    if not bidder:
        raise HTTPException(status_code=404, detail="Bidder not found")

    result = ComplianceEngine.run_full_verification(
        db=db,
        bidder_id=id,
        officer_id=current_user.id,
        officer_name=current_user.name
    )
    return result
