import os
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

router = APIRouter(prefix="/bidders", tags=["Bidders"])

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

@router.post("", response_model=BidderResponse)
def create_bidder(
    bidder_in: BidderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tender = db.query(Tender).filter(Tender.id == bidder_in.tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    bidder = Bidder(
        tender_id=bidder_in.tender_id,
        legal_name=bidder_in.legal_name,
        trade_name=bidder_in.trade_name,
        gstin=bidder_in.gstin,
        pan=bidder_in.pan,
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
        new_state={"legal_name": bidder.legal_name, "gstin": bidder.gstin},
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

@router.get("/{id}", response_model=BidderDetailResponse)
def get_bidder(id: str, db: Session = Depends(get_db)):
    bidder = db.query(Bidder).filter(Bidder.id == id).first()
    if not bidder:
        raise HTTPException(status_code=404, detail="Bidder not found")

    score_val = bidder.compliance_score.overall_score if bidder.compliance_score else None
    risk_val = bidder.risk_assessment.risk_level if bidder.risk_assessment else None
    rec_val = bidder.recommendation.recommendation_type if bidder.recommendation else None

    # Load projects and personnel
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
