from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import ComplianceCheck, OfficerReview, Bidder, User, Requirement
from app.schemas.schemas import OfficerReviewCreate, OfficerReviewResponse, ComplianceCheckResponse
from app.api.deps import get_current_user
from app.audit.audit_service import AuditService
from app.scoring import ComplianceScorer, RiskEngine, RecommendationGenerator

router = APIRouter(prefix="/compliance", tags=["Compliance & Officer Reviews"])

@router.post("/{check_id}/review", response_model=OfficerReviewResponse)
def review_compliance_check(
    check_id: str,
    review_in: OfficerReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check = db.query(ComplianceCheck).filter(ComplianceCheck.id == check_id).first()
    if not check:
        raise HTTPException(status_code=404, detail="Compliance check record not found")

    bidder = db.query(Bidder).filter(Bidder.id == check.bidder_id).first()
    prev_status = check.status
    
    # Update check status based on officer decision
    check.status = review_in.new_status
    check.reason = f"[OFFICER {review_in.action_type}]: {review_in.remarks} (Original AI note: {check.reason})"
    
    # Save Officer Review record
    review = OfficerReview(
        bidder_id=bidder.id,
        requirement_id=check.requirement_id,
        officer_id=current_user.id,
        officer_name=current_user.full_name,
        previous_status=prev_status,
        new_status=review_in.new_status,
        action_type=review_in.action_type,
        remarks=review_in.remarks,
        reviewed_at=datetime.now(timezone.utc)
    )
    db.add(review)

    # Recalculate score and risk after officer override
    all_checks = db.query(ComplianceCheck).filter(ComplianceCheck.bidder_id == bidder.id).all()
    checks_list = []
    for c in all_checks:
        checks_list.append({
            "requirement_category": c.requirement.category if c.requirement else "GENERAL",
            "requirement_mandatory": c.requirement.mandatory if c.requirement else True,
            "status": c.status,
            "confidence": c.confidence,
            "reason": c.reason
        })

    score_data = ComplianceScorer.calculate_score(checks_list)
    risk_data = RiskEngine.assess_risk(checks_list, score_data["overall_score"])
    rec_data = RecommendationGenerator.generate_recommendation(
        bidder.bidder_name, checks_list, score_data["overall_score"], risk_data["risk_level"]
    )

    if bidder.compliance_score:
        bidder.compliance_score.overall_score = score_data["overall_score"]
        bidder.compliance_score.statutory_score = score_data["statutory_score"]
        bidder.compliance_score.financial_score = score_data["financial_score"]
        bidder.compliance_score.tender_specific_score = score_data["tender_specific_score"]
    
    if bidder.risk_assessment:
        bidder.risk_assessment.risk_level = risk_data["risk_level"]
        bidder.risk_assessment.primary_risk_factors = risk_data["primary_risk_factors"]
        bidder.risk_assessment.risk_score = risk_data["risk_score"]

    if bidder.recommendation:
        bidder.recommendation.recommendation_type = rec_data["recommendation_type"]
        bidder.recommendation.summary = rec_data["summary"]
        bidder.recommendation.detailed_reasons = rec_data["detailed_reasons"]

    # If all items reviewed, update status
    has_reviews = any(c.status == "REVIEW" for c in all_checks)
    bidder.status = "FINALIZED" if not has_reviews else "UNDER_REVIEW"

    db.commit()
    db.refresh(review)

    # Audit log
    AuditService.log_action(
        db=db,
        action=f"OFFICER_{review_in.action_type}",
        entity_type="COMPLIANCE_CHECK",
        entity_id=check.id,
        user_id=current_user.id,
        user_name=current_user.full_name,
        tender_id=bidder.tender_id,
        bidder_id=bidder.id,
        previous_state={"status": prev_status},
        new_state={"status": review_in.new_status, "remarks": review_in.remarks},
        reason=review_in.remarks
    )

    return review

@router.get("/reviews/pending", response_model=List[ComplianceCheckResponse])
def get_pending_review_queue(db: Session = Depends(get_db)):
    pending = db.query(ComplianceCheck).filter(ComplianceCheck.status == "REVIEW").all()
    results = []
    for c in pending:
        results.append({
            "id": c.id,
            "bidder_id": c.bidder_id,
            "requirement_id": c.requirement_id,
            "requirement_category": c.requirement.category if c.requirement else "GENERAL",
            "requirement_description": c.requirement.description if c.requirement else "",
            "requirement_mandatory": c.requirement.mandatory if c.requirement else True,
            "status": c.status,
            "confidence": c.confidence,
            "score_contribution": c.score_contribution,
            "reason": c.reason,
            "evidence_text": c.evidence_text,
            "document_id": c.document_id,
            "document_name": c.document_name,
            "page_number": c.page_number,
            "verification_source": c.verification_source,
            "verification_method": c.verification_method,
            "rule_version": c.rule_version,
            "verified_at": c.verified_at,
            "evidence_items": c.evidence_items
        })
    return results
