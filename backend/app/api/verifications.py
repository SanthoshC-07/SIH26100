from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, verify_bidder_ownership
from app.models.models import ComplianceCheck, Bidder, Requirement, User
from app.schemas.schemas import ComplianceCheckResponse

router = APIRouter(prefix="/verifications", tags=["Verifications"])

@router.get("", response_model=List[ComplianceCheckResponse])
def list_verifications(
    bidder_id: Optional[str] = None,
    requirement_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(ComplianceCheck)
    if current_user.role == "BIDDER":
        # Strictly scope to bidder's own verifications
        query = query.filter(ComplianceCheck.bidder_id == current_user.effective_bidder_id)
    elif bidder_id:
        query = query.filter(ComplianceCheck.bidder_id == bidder_id)

    if requirement_id:
        query = query.filter(ComplianceCheck.requirement_id == requirement_id)
    if status:
        query = query.filter(ComplianceCheck.status == status)
    return query.order_by(ComplianceCheck.created_at.desc()).all()

@router.get("/{id}", response_model=ComplianceCheckResponse)
def get_verification(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check = db.query(ComplianceCheck).filter(ComplianceCheck.id == id).first()
    if not check:
        raise HTTPException(status_code=404, detail="Verification check not found")
    if check.bidder_id:
        verify_bidder_ownership(check.bidder_id, current_user, db)
    return check
