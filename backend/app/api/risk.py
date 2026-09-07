from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Bidder, Bid, RiskAssessment, RiskFactor, ComplianceCheck, User
from app.api.deps import require_any_role
from app.scoring.risk_engine import RiskEngine

router = APIRouter(prefix="/risk", tags=["Risk Analysis Engine"])

def _resolve_bidder(bid_id: str, db: Session) -> Bidder:
    bidder = db.query(Bidder).filter(Bidder.id == bid_id).first()
    if bidder:
        return bidder
    bid = db.query(Bid).filter(Bid.id == bid_id).first()
    if bid and bid.bidder:
        return bid.bidder
    elif bid:
        bidder = db.query(Bidder).filter(Bidder.id == bid.bidder_id).first()
        if bidder:
            return bidder
    raise HTTPException(status_code=404, detail=f"Bid or Bidder record '{bid_id}' not found")

@router.get("/{bid_id}")
def get_bid_risk_assessment(
    bid_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role("PROCUREMENT_OFFICER", "ADMIN"))
):
    """
    Returns complete multi-factor risk assessment, score, and granular risk factors for a bid.
    Procurement Officers and Admins have full access.
    Bidders are isolated from internal risk details.
    """
    # RBAC protection: Bidder cannot inspect internal risk analytics intended for officers
    if current_user and current_user.role == "BIDDER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted: Internal risk analysis is reserved for Procurement Officers and Oversight Authorities."
        )

    bidder = _resolve_bidder(bid_id, db)

    assessment = db.query(RiskAssessment).filter(RiskAssessment.bidder_id == bidder.id).first()
    factors = db.query(RiskFactor).filter(RiskFactor.bid_id == bidder.id).all()

    if not assessment:
        # Calculate dynamically if not yet stored
        return calculate_bid_risk(bid_id, db, current_user)

    factors_data = [
        {
            "id": f.id,
            "factor_type": f.factor_type,
            "severity": f.severity,
            "description": f.description,
            "requirement_id": f.requirement_id,
            "compliance_check_id": f.compliance_check_id,
            "evidence_snippet": f.evidence_snippet,
            "source_document": f.source_document,
            "page_number": f.page_number,
            "created_at": f.created_at.isoformat() if f.created_at else None
        }
        for f in factors
    ]

    return {
        "bidder_id": bidder.id,
        "bidder_name": bidder.legal_name or bidder.bidder_name,
        "risk_level": assessment.risk_level,
        "risk_score": assessment.risk_score,
        "primary_risk_factors": assessment.primary_risk_factors or [],
        "factors": factors_data,
        "assessed_at": assessment.assessed_at.isoformat() if assessment.assessed_at else None
    }

@router.post("/{bid_id}/calculate")
def calculate_bid_risk(
    bid_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role("PROCUREMENT_OFFICER", "ADMIN"))
):
    """
    Recomputes multi-factor risk assessment based on latest compliance checks and cross-document telemetry,
    and updates SQLite records.
    """
    bidder = _resolve_bidder(bid_id, db)

    checks = db.query(ComplianceCheck).filter(ComplianceCheck.bidder_id == bidder.id).all()
    checks_list = []
    for c in checks:
        checks_list.append({
            "requirement_id": c.requirement_id,
            "compliance_check_id": c.id,
            "category": c.requirement.category if c.requirement else "GENERAL",
            "requirement_category": c.requirement.category if c.requirement else "GENERAL",
            "mandatory": c.requirement.mandatory if c.requirement else True,
            "requirement_mandatory": c.requirement.mandatory if c.requirement else True,
            "status": c.status,
            "confidence": c.confidence,
            "reason": c.reason,
            "source_document": c.document_name,
            "page_number": c.page_number,
            "evidence": c.evidence_text
        })

    overall_score = bidder.compliance_score.overall_score if bidder.compliance_score else 85.0
    risk_data = RiskEngine.assess_risk(checks_list, overall_score=overall_score)
    RiskEngine.persist_risk_factors(db, bidder.id, risk_data)

    factors = db.query(RiskFactor).filter(RiskFactor.bid_id == bidder.id).all()
    factors_data = [
        {
            "id": f.id,
            "factor_type": f.factor_type,
            "severity": f.severity,
            "description": f.description,
            "requirement_id": f.requirement_id,
            "compliance_check_id": f.compliance_check_id,
            "evidence_snippet": f.evidence_snippet,
            "source_document": f.source_document,
            "page_number": f.page_number,
            "created_at": f.created_at.isoformat() if f.created_at else None
        }
        for f in factors
    ]

    return {
        "bidder_id": bidder.id,
        "bidder_name": bidder.legal_name or bidder.bidder_name,
        "risk_level": risk_data["risk_level"],
        "risk_score": risk_data["risk_score"],
        "primary_risk_factors": risk_data["primary_risk_factors"],
        "factors": factors_data,
        "assessed_at": risk_data["assessed_at"]
    }
