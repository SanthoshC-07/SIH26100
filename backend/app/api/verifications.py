from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import ComplianceCheck, Bidder, Requirement
from app.schemas.schemas import ComplianceCheckResponse

router = APIRouter(prefix="/verifications", tags=["Verifications"])

@router.get("", response_model=List[ComplianceCheckResponse])
def list_verifications(
    bidder_id: Optional[str] = None,
    requirement_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ComplianceCheck)
    if bidder_id:
        query = query.filter(ComplianceCheck.bidder_id == bidder_id)
    if requirement_id:
        query = query.filter(ComplianceCheck.requirement_id == requirement_id)
    if status:
        query = query.filter(ComplianceCheck.status == status)
    return query.order_by(ComplianceCheck.created_at.desc()).all()

@router.get("/{id}", response_model=ComplianceCheckResponse)
def get_verification(id: str, db: Session = Depends(get_db)):
    check = db.query(ComplianceCheck).filter(ComplianceCheck.id == id).first()
    if not check:
        raise HTTPException(status_code=404, detail="Verification check not found")
    return check
