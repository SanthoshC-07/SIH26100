import os
import shutil
import uuid
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models.models import Tender, Requirement, User, Document
from app.schemas.schemas import (
    TenderCreate, TenderUpdate, TenderResponse,
    RequirementCreate, RequirementResponse, DocumentResponse
)
from app.api.deps import get_current_user
from app.documents.extractor import DocumentExtractor
from app.ml.requirement_parser import TenderRequirementParser
from app.audit.audit_service import AuditService

router = APIRouter(prefix="/tenders", tags=["Tenders"])

@router.get("", response_model=List[TenderResponse])
def list_tenders(
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Tender)
    if status_filter:
        query = query.filter(Tender.status == status_filter.upper())
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Tender.tender_number.ilike(search_pattern)) |
            (Tender.title.ilike(search_pattern)) |
            (Tender.issuing_organization.ilike(search_pattern))
        )
    
    tenders = query.order_by(Tender.created_at.desc()).offset(skip).limit(limit).all()
    results = []
    for t in tenders:
        results.append({
            "id": t.id,
            "tender_number": t.tender_number,
            "title": t.title,
            "organization": t.organization,
            "category": t.category,
            "description": t.description,
            "estimated_value": t.estimated_value,
            "issue_date": t.issue_date,
            "submission_deadline": t.submission_deadline,
            "status": t.status,
            "raw_pdf_path": t.raw_pdf_path,
            "created_by": t.created_by,
            "created_at": t.created_at,
            "updated_at": t.updated_at,
            "requirements_count": len(t.requirements),
            "bidders_count": len(t.bidders)
        })
    return results

@router.post("", response_model=TenderResponse, status_code=status.HTTP_201_CREATED)
def create_tender(
    tender_in: TenderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Unique tender_number validation
    existing = db.query(Tender).filter(Tender.tender_number == tender_in.tender_number.strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tender number '{tender_in.tender_number}' is already registered."
        )

    # Submission deadline validation
    if tender_in.submission_deadline and tender_in.issue_date:
        if tender_in.submission_deadline <= tender_in.issue_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Submission deadline must be after the issue date."
            )

    tender = Tender(
        tender_number=tender_in.tender_number.strip(),
        title=tender_in.title.strip(),
        issuing_organization=(tender_in.issuing_organization or tender_in.organization or "GAIL (India) Limited").strip(),
        ministry=tender_in.ministry or "Ministry of Petroleum & Natural Gas",
        sector=tender_in.sector or "OIL_AND_GAS",
        tender_type=tender_in.tender_type or "PIPELINE_PROCUREMENT",
        project_type=tender_in.project_type or "PIPELINE_CONSTRUCTION",
        pipeline_type=tender_in.pipeline_type or "CROSS_COUNTRY_PIPELINE",
        location=tender_in.location or "National Gas Grid, India",
        category=tender_in.category or "Petroleum & Pipeline Infrastructure",
        description=tender_in.description,
        estimated_value=tender_in.estimated_value,
        tender_issue_date=tender_in.tender_issue_date or tender_in.issue_date or datetime.now(timezone.utc),
        submission_deadline=tender_in.submission_deadline,
        status=tender_in.status.upper(),
        created_by=current_user.id
    )
    db.add(tender)
    db.flush()

    if tender_in.requirements:
        for r in tender_in.requirements:
            req = Requirement(
                tender_id=tender.id,
                category=r.category.upper(),
                clause_number=r.clause_number,
                description=r.description,
                threshold=r.threshold,
                threshold_unit=r.threshold_unit,
                period=r.period,
                mandatory=r.mandatory,
                evidence_required=r.evidence_required,
                verification_method=r.verification_method,
                rule_version=r.rule_version
            )
            db.add(req)

    db.commit()
    db.refresh(tender)

    AuditService.log_action(
        db=db,
        action="TENDER_CREATED",
        entity_type="TENDER",
        entity_id=tender.id,
        user_id=current_user.id,
        user_name=current_user.name,
        tender_id=tender.id,
        new_state={"tender_number": tender.tender_number, "title": tender.title, "status": tender.status},
        reason=f"Created tender {tender.tender_number} ({tender.title})"
    )

    return {
        "id": tender.id,
        "tender_number": tender.tender_number,
        "title": tender.title,
        "organization": tender.organization,
        "category": tender.category,
        "description": tender.description,
        "estimated_value": tender.estimated_value,
        "issue_date": tender.issue_date,
        "submission_deadline": tender.submission_deadline,
        "status": tender.status,
        "raw_pdf_path": tender.raw_pdf_path,
        "created_by": tender.created_by,
        "created_at": tender.created_at,
        "updated_at": tender.updated_at,
        "requirements_count": len(tender.requirements),
        "bidders_count": 0
    }

@router.get("/{id}", response_model=TenderResponse)
def get_tender(id: str, db: Session = Depends(get_db)):
    tender = db.query(Tender).filter(Tender.id == id).first()
    if not tender:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tender not found")
    
    return {
        "id": tender.id,
        "tender_number": tender.tender_number,
        "title": tender.title,
        "organization": tender.organization,
        "category": tender.category,
        "description": tender.description,
        "estimated_value": tender.estimated_value,
        "issue_date": tender.issue_date,
        "submission_deadline": tender.submission_deadline,
        "status": tender.status,
        "raw_pdf_path": tender.raw_pdf_path,
        "created_by": tender.created_by,
        "created_at": tender.created_at,
        "updated_at": tender.updated_at,
        "requirements_count": len(tender.requirements),
        "bidders_count": len(tender.bidders)
    }

@router.put("/{id}", response_model=TenderResponse)
def update_tender(
    id: str,
    tender_update: TenderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tender = db.query(Tender).filter(Tender.id == id).first()
    if not tender:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tender not found")

    prev_state = {
        "title": tender.title,
        "status": tender.status,
        "estimated_value": tender.estimated_value
    }

    if tender_update.title is not None:
        tender.title = tender_update.title.strip()
    if tender_update.organization is not None:
        tender.organization = tender_update.organization.strip()
    if tender_update.category is not None:
        tender.category = tender_update.category
    if tender_update.description is not None:
        tender.description = tender_update.description
    if tender_update.estimated_value is not None:
        tender.estimated_value = tender_update.estimated_value
    if tender_update.submission_deadline is not None:
        if tender.issue_date and tender_update.submission_deadline <= tender.issue_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Submission deadline must be after the issue date."
            )
        tender.submission_deadline = tender_update.submission_deadline
    if tender_update.status is not None:
        valid_statuses = ["DRAFT", "ACTIVE", "UNDER_REVIEW", "CLOSED"]
        if tender_update.status.upper() not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Status must be one of {valid_statuses}"
            )
        tender.status = tender_update.status.upper()

    tender.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(tender)

    AuditService.log_action(
        db=db,
        action="TENDER_UPDATED",
        entity_type="TENDER",
        entity_id=tender.id,
        user_id=current_user.id,
        user_name=current_user.name,
        tender_id=tender.id,
        previous_state=prev_state,
        new_state={"title": tender.title, "status": tender.status, "estimated_value": tender.estimated_value},
        reason=f"Updated tender {tender.tender_number}"
    )

    return {
        "id": tender.id,
        "tender_number": tender.tender_number,
        "title": tender.title,
        "organization": tender.organization,
        "category": tender.category,
        "description": tender.description,
        "estimated_value": tender.estimated_value,
        "issue_date": tender.issue_date,
        "submission_deadline": tender.submission_deadline,
        "status": tender.status,
        "raw_pdf_path": tender.raw_pdf_path,
        "created_by": tender.created_by,
        "created_at": tender.created_at,
        "updated_at": tender.updated_at,
        "requirements_count": len(tender.requirements),
        "bidders_count": len(tender.bidders)
    }

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_tender(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tender = db.query(Tender).filter(Tender.id == id).first()
    if not tender:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tender not found")

    tender_num = tender.tender_number
    db.delete(tender)
    db.commit()

    AuditService.log_action(
        db=db,
        action="TENDER_DELETED",
        entity_type="TENDER",
        entity_id=id,
        user_id=current_user.id,
        user_name=current_user.name,
        reason=f"Deleted tender {tender_num}"
    )

    return {"message": f"Tender {tender_num} deleted successfully", "id": id}

@router.post("/{id}/documents", response_model=DocumentResponse)
async def upload_tender_document(
    id: str,
    file: UploadFile = File(...),
    document_type: str = Form("TENDER_SPECIFICATION"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tender = db.query(Tender).filter(Tender.id == id).first()
    if not tender:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tender not found")

    original_filename = file.filename or "tender_document.pdf"
    file_ext = os.path.splitext(original_filename)[1].lower()

    # File extension validation
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension '{file_ext}'. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # MIME type validation
    content_type = file.content_type or "application/octet-stream"
    if content_type not in settings.ALLOWED_MIME_TYPES and file_ext != ".pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid MIME type '{content_type}' for uploaded file."
        )

    # Safe unique filename generation
    safe_filename = f"tender_{tender.id}_{uuid.uuid4().hex[:8]}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    # Read and validate file size
    contents = await file.read()
    file_size = len(contents)
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size ({file_size / (1024*1024):.2f} MB) exceeds maximum allowed limit of {settings.MAX_FILE_SIZE_MB} MB."
        )

    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    tender.raw_pdf_path = file_path

    # Extract text and parse requirements automatically
    extracted = DocumentExtractor.extract_document(file_path)
    full_text = extracted.get("full_text", "")

    doc = Document(
        tender_id=tender.id,
        document_name=safe_filename,
        original_filename=original_filename,
        document_type=document_type,
        file_path=file_path,
        file_size=file_size,
        mime_type=content_type,
        is_scanned=extracted["is_scanned"],
        page_count=extracted["page_count"],
        extracted_text=full_text,
        uploaded_by=current_user.id,
        upload_timestamp=datetime.now(timezone.utc)
    )
    db.add(doc)

    parsed_reqs = TenderRequirementParser.parse_clauses_from_text(full_text)
    if parsed_reqs:
        db.query(Requirement).filter(Requirement.tender_id == tender.id).delete()
        for r in parsed_reqs:
            req = Requirement(
                tender_id=tender.id,
                category=r["category"],
                clause_number=r.get("clause_number"),
                description=r["description"],
                threshold=r.get("threshold"),
                threshold_unit=r.get("threshold_unit"),
                period=r.get("period"),
                mandatory=r.get("mandatory", True),
                evidence_required=r.get("evidence_required", []),
                verification_method=r.get("verification_method", "RULE_AND_PORTAL"),
                rule_version=r.get("rule_version", "1.0")
            )
            db.add(req)

    db.commit()
    db.refresh(doc)

    AuditService.log_action(
        db=db,
        action="TENDER_DOCUMENT_UPLOADED",
        entity_type="DOCUMENT",
        entity_id=doc.id,
        user_id=current_user.id,
        user_name=current_user.name,
        tender_id=tender.id,
        new_state={"original_filename": original_filename, "file_size": file_size, "requirements_extracted": len(parsed_reqs)},
        reason=f"Uploaded specification document '{original_filename}' and extracted {len(parsed_reqs)} compliance requirements"
    )

    return {
        "id": doc.id,
        "bidder_id": None,
        "tender_id": tender.id,
        "document_name": doc.document_name,
        "original_filename": doc.original_filename,
        "document_type": doc.document_type,
        "file_size": doc.file_size,
        "mime_type": doc.mime_type,
        "is_scanned": doc.is_scanned,
        "page_count": doc.page_count,
        "uploaded_by": doc.uploaded_by,
        "upload_timestamp": doc.upload_timestamp,
        "entities_count": 0
    }

@router.get("/{id}/requirements", response_model=List[RequirementResponse])
def get_tender_requirements(id: str, db: Session = Depends(get_db)):
    tender = db.query(Tender).filter(Tender.id == id).first()
    if not tender:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tender not found")
    return tender.requirements

@router.post("/{id}/requirements", response_model=RequirementResponse)
def add_tender_requirement(
    id: str,
    req_in: RequirementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tender = db.query(Tender).filter(Tender.id == id).first()
    if not tender:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tender not found")

    req = Requirement(
        tender_id=tender.id,
        category=req_in.category.upper(),
        clause_number=req_in.clause_number or f"Cl-{len(tender.requirements)+1}",
        description=req_in.description,
        threshold=req_in.threshold,
        threshold_unit=req_in.threshold_unit,
        period=req_in.period,
        mandatory=req_in.mandatory,
        evidence_required=req_in.evidence_required,
        verification_method=req_in.verification_method,
        rule_version=req_in.rule_version
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req
