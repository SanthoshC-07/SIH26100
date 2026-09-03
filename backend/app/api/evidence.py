from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Evidence, ComplianceCheck
from app.schemas.schemas import EvidenceResponse

router = APIRouter(prefix="/evidence", tags=["Evidence"])

@router.get("", response_model=List[EvidenceResponse])
def list_evidence(
    compliance_check_id: Optional[str] = None,
    document_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Evidence)
    if compliance_check_id:
        query = query.filter(Evidence.compliance_check_id == compliance_check_id)
    if document_id:
        query = query.filter(Evidence.document_id == document_id)
    return query.order_by(Evidence.created_at.desc()).all()

@router.get("/{id}", response_model=EvidenceResponse)
def get_evidence_item(id: str, db: Session = Depends(get_db)):
    ev = db.query(Evidence).filter(Evidence.id == id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence item not found")
    return ev
