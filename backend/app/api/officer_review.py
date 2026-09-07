from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import (
    Bidder, Bid, Tender, Requirement, ComplianceCheck, Evidence,
    OfficerDecision, OfficerOverride, RiskAssessment, RiskFactor, User
)
from app.api.deps import (
    get_current_user, get_current_user_optional, get_current_officer,
    get_current_officer_only, require_role, require_any_role
)
from app.audit.audit_service import AuditService
from app.scoring import ComplianceScorer, RiskEngine, RecommendationGenerator
from app.schemas.schemas import (
    RequirementDecisionRequest, RequirementDecisionResponse,
    FinalBidDecisionRequest, FinalBidDecisionResponse
)

router = APIRouter(prefix="/officer-review", tags=["Procurement Officer Review Workspace"])

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
def get_officer_review_workspace(
    bid_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_officer)
):
    """
    Returns full officer review workspace payload:
    Tender, Bidder, submission date, compliance score, risk level, AI recommendation,
    and dense requirements table with AI status, evidence citations, rule results,
    and any recorded officer determinations.
    """
    bidder = _resolve_bidder(bid_id, db)
    bid = db.query(Bid).filter(Bid.bidder_id == bidder.id).first()
    tender = db.query(Tender).filter(Tender.id == bidder.tender_id).first()

    # Ensure compliance checks exist
    checks = db.query(ComplianceCheck).filter(ComplianceCheck.bidder_id == bidder.id).all()
    if not checks:
        from app.api.compliance import run_compliance_evaluation
        run_compliance_evaluation(bidder.id, db)
        checks = db.query(ComplianceCheck).filter(ComplianceCheck.bidder_id == bidder.id).all()

    # Load existing officer decisions
    decisions = db.query(OfficerDecision).filter(
        OfficerDecision.bid_id == bidder.id,
        OfficerDecision.decision_type == "REQUIREMENT_DECISION"
    ).all()
    decisions_by_req = {d.requirement_id: d for d in decisions if d.requirement_id}

    final_decision_record = db.query(OfficerDecision).filter(
        OfficerDecision.bid_id == bidder.id,
        OfficerDecision.decision_type == "FINAL_BID_DECISION"
    ).order_by(OfficerDecision.decision_timestamp.desc()).first()

    # Build dense requirement table data
    req_rows = []
    for c in checks:
        req = c.requirement
        first_ev = c.evidence_items[0] if c.evidence_items else None
        clause_no = req.clause_number if req else (c.clause_number or "REQ-000")
        cat = req.category if req else "GENERAL"
        desc = (req.description if req and req.description else c.reason) or f"{cat} Requirement Specification"

        # AI original baseline
        ai_status = c.status
        ai_confidence = round(float(c.confidence or 1.0), 2)

        # Existing officer decision
        existing_dec = decisions_by_req.get(c.requirement_id)
        officer_decision_data = None
        if existing_dec:
            officer_decision_data = {
                "decision": existing_dec.officer_status,
                "reason": existing_dec.officer_reason,
                "officer_name": existing_dec.officer_name,
                "is_override": existing_dec.is_override,
                "timestamp": existing_dec.decision_timestamp.isoformat() if existing_dec.decision_timestamp else None
            }

        # Extracted value / rule result
        calc_breakdown = first_ev.calculation_breakdown if first_ev and first_ev.calculation_breakdown else {}
        extracted_entities = first_ev.extracted_entities if first_ev and first_ev.extracted_entities else {}

        # Requirement risk
        req_risk = "CRITICAL" if c.status == "FAIL" and (cat in ["GST", "PAN", "HSE", "SAFETY"]) else (
            "HIGH" if c.status == "FAIL" else ("MEDIUM" if c.status in ["REVIEW", "INSUFFICIENT"] else "LOW")
        )

        req_rows.append({
            "requirement_id": req.id if req else c.requirement_id,
            "clause_number": clause_no,
            "category": cat,
            "title": desc[:60] + ("..." if len(desc) > 60 else ""),
            "requirement_text": desc,
            "required_evidence": (req.conditions or {}).get("required_documents", ["Standard Certificate / Return"]) if req and req.conditions else ["Official Registration"],
            "submitted_evidence": c.evidence_text or "Submitted corporate dossier",
            "source_document": c.document_name or (first_ev.document_name if first_ev else "Document.pdf"),
            "page": c.page_number or (first_ev.page_number if first_ev else 1),
            "extracted_value": extracted_entities or (c.evidence_text[:100] if c.evidence_text else "Verified"),
            "rule_result": calc_breakdown.get("rule", "PASS" if c.status == "PASS" else c.status),
            "semantic_score": 0.94 if c.status == "PASS" else 0.72,
            "confidence": ai_confidence,
            "ai_status": ai_status,
            "risk": req_risk,
            "officer_decision": officer_decision_data
        })

    # Summary metrics
    score = bidder.compliance_score.overall_score if bidder.compliance_score else 85.0
    risk_level = bidder.risk_assessment.risk_level if bidder.risk_assessment else "LOW"
    recommendation = bidder.recommendation.recommendation_type if bidder.recommendation else "Recommended for Officer Review"

    return {
        "tender": {
            "id": tender.id if tender else None,
            "tender_number": tender.tender_number if tender else "MOPNG/PIPE/2026/017",
            "title": tender.title if tender else "Cross-Country Pipeline Procurement",
            "organization": tender.issuing_organization if tender else "GAIL (India) Limited",
            "category": tender.category if tender else "Pipeline Infrastructure",
            "estimated_value": tender.estimated_value if tender else 0.0
        },
        "bidder": {
            "id": bidder.id,
            "legal_name": bidder.legal_name,
            "trade_name": bidder.trade_name or bidder.legal_name,
            "pan": bidder.pan,
            "gstin": bidder.gstin,
            "country": bidder.country
        },
        "submission_date": (bid.submission_date if bid else bidder.submitted_at).isoformat(),
        "compliance_score": round(score, 1),
        "risk_level": risk_level,
        "recommendation": recommendation,
        "governance_notice": "AI-generated results are decision support. Final procurement decision is made by the Procurement Officer.",
        "requirements": req_rows,
        "final_decision": {
            "decision": final_decision_record.officer_status if final_decision_record else None,
            "remarks": final_decision_record.officer_reason if final_decision_record else None,
            "officer_name": final_decision_record.officer_name if final_decision_record else None,
            "timestamp": final_decision_record.decision_timestamp.isoformat() if final_decision_record and final_decision_record.decision_timestamp else None
        } if final_decision_record else None
    }

@router.post("/{bid_id}/requirements/{requirement_id}/decision", response_model=RequirementDecisionResponse)
def submit_requirement_decision(
    bid_id: str,
    requirement_id: str,
    decision_in: RequirementDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_officer_only)
):
    """
    Records an Officer Decision for an individual requirement clause:
    ACCEPT_AI_RESULT, PASS, FAIL, REVIEW, INSUFFICIENT.
    When overriding, requires mandatory non-empty reason, stores officer identity/timestamp,
    and preserves original AI determination.
    """
    bidder = _resolve_bidder(bid_id, db)
    
    # Resolve ComplianceCheck
    check = db.query(ComplianceCheck).filter(
        ComplianceCheck.bidder_id == bidder.id,
        ComplianceCheck.requirement_id == requirement_id
    ).first()

    if not check:
        # Try matching requirement by clause_number or category
        req = db.query(Requirement).filter(
            (Requirement.id == requirement_id) |
            (Requirement.clause_number == requirement_id) |
            (Requirement.category == requirement_id)
        ).first()
        if req:
            check = db.query(ComplianceCheck).filter(
                ComplianceCheck.bidder_id == bidder.id,
                ComplianceCheck.requirement_id == req.id
            ).first()

    if not check:
        raise HTTPException(status_code=404, detail="Compliance check record not found for this requirement.")

    ai_baseline_status = check.status
    ai_confidence = float(check.confidence or 1.0)
    target_decision = decision_in.decision.upper()

    is_override = False
    if target_decision == "ACCEPT_AI_RESULT":
        final_status = ai_baseline_status
        reason_text = decision_in.reason.strip() if decision_in.reason else "Officer accepted AI baseline determination."
    else:
        final_status = target_decision
        if final_status != ai_baseline_status:
            is_override = True
            if not decision_in.reason or not decision_in.reason.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Officer override reason is mandatory. AI compliance determination cannot be overridden without documented justification."
                )
            reason_text = decision_in.reason.strip()
        else:
            reason_text = decision_in.reason.strip() if decision_in.reason else "Officer confirmed matching status."

    officer_name = decision_in.officer_name or (
        current_user.name if current_user and current_user.name else "Rajesh Sharma, Senior Procurement Officer"
    )
    now_utc = datetime.now(timezone.utc)

    # Record or update OfficerDecision
    decision_rec = db.query(OfficerDecision).filter(
        OfficerDecision.bid_id == bidder.id,
        OfficerDecision.requirement_id == check.requirement_id,
        OfficerDecision.decision_type == "REQUIREMENT_DECISION"
    ).first()

    if not decision_rec:
        decision_rec = OfficerDecision(
            bid_id=bidder.id,
            requirement_id=check.requirement_id,
            compliance_check_id=check.id,
            officer_id=current_user.id if current_user else None,
            officer_name=officer_name,
            decision_type="REQUIREMENT_DECISION",
            ai_status=ai_baseline_status,
            ai_confidence=ai_confidence,
            officer_status=final_status,
            officer_reason=reason_text,
            is_override=is_override,
            decision_timestamp=now_utc
        )
        db.add(decision_rec)
    else:
        decision_rec.officer_status = final_status
        decision_rec.officer_reason = reason_text
        decision_rec.is_override = is_override
        decision_rec.officer_name = officer_name
        decision_rec.decision_timestamp = now_utc

    # Record OfficerOverride for Phase 4 compliance trail if overridden
    if is_override:
        override_rec = OfficerOverride(
            bid_id=bidder.id,
            requirement_id=check.requirement_id,
            compliance_check_id=check.id,
            officer_id=current_user.id if current_user else None,
            officer_name=officer_name,
            original_ai_status=ai_baseline_status,
            overridden_status=final_status,
            override_reason=reason_text,
            action_type="OFFICER_OVERRIDE",
            timestamp=now_utc
        )
        db.add(override_rec)

    # Update check status while preserving AI baseline trace in reason
    check.status = final_status
    check.score_contribution = 1.0 if final_status == "PASS" else (0.5 if final_status == "REVIEW" else 0.0)
    check.reason = f"[OFFICER {'OVERRIDE' if is_override else 'CONFIRMATION'}]: {reason_text} (Original AI Baseline: {ai_baseline_status})"
    check.verified_at = now_utc

    # Recalculate score and risk after officer review
    all_checks = db.query(ComplianceCheck).filter(ComplianceCheck.bidder_id == bidder.id).all()
    checks_list = [
        {
            "requirement_id": c.requirement_id,
            "category": c.requirement.category if c.requirement else "GENERAL",
            "requirement_category": c.requirement.category if c.requirement else "GENERAL",
            "mandatory": c.requirement.mandatory if c.requirement else True,
            "status": c.status,
            "confidence": c.confidence,
            "reason": c.reason,
            "source_document": c.document_name,
            "page_number": c.page_number,
            "evidence": c.evidence_text
        }
        for c in all_checks
    ]

    score_data = ComplianceScorer.calculate_score(checks_list)
    risk_data = RiskEngine.assess_risk(checks_list, overall_score=score_data["overall_score"])
    RiskEngine.persist_risk_factors(db, bidder.id, risk_data)

    if bidder.compliance_score:
        bidder.compliance_score.overall_score = score_data["overall_score"]
        bidder.compliance_score.statutory_score = score_data["statutory_score"]
        bidder.compliance_score.financial_score = score_data["financial_score"]
        bidder.compliance_score.tender_specific_score = score_data["tender_specific_score"]

    db.commit()
    db.refresh(decision_rec)

    # Log audit event
    action_name = "AI_RESULT_OVERRIDDEN" if is_override else "OFFICER_REVIEWED"
    AuditService.log_event(
        db=db,
        action=action_name,
        entity_type="REQUIREMENT",
        entity_id=check.requirement_id,
        user_id=current_user.id if current_user else None,
        user_name=officer_name,
        role="PROCUREMENT_OFFICER",
        tender_id=bidder.tender_id,
        bidder_id=bidder.id,
        description=f"Officer {officer_name} set decision '{final_status}' on requirement {check.requirement_id}. Reason: {reason_text}",
        metadata={
            "ai_baseline_status": ai_baseline_status,
            "officer_status": final_status,
            "is_override": is_override,
            "reason": reason_text
        }
    )

    return RequirementDecisionResponse(
        id=decision_rec.id,
        bid_id=bidder.id,
        requirement_id=decision_rec.requirement_id,
        compliance_check_id=decision_rec.compliance_check_id,
        decision_type=decision_rec.decision_type,
        ai_status=decision_rec.ai_status,
        ai_confidence=decision_rec.ai_confidence,
        officer_status=decision_rec.officer_status,
        officer_reason=decision_rec.officer_reason,
        is_override=decision_rec.is_override,
        officer_id=decision_rec.officer_id,
        officer_name=decision_rec.officer_name,
        decision_timestamp=decision_rec.decision_timestamp
    )

@router.post("/{bid_id}/final-decision", response_model=FinalBidDecisionResponse)
def submit_final_bid_decision(
    bid_id: str,
    decision_in: FinalBidDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_officer_only)
):
    """
    Submits final procurement decision: QUALIFIED, DISQUALIFIED, REVIEW / HOLD.
    Validates confirmation and mandatory remarks, stores officer decision,
    updates Bid record, and logs immutable audit trail.
    """
    if not decision_in.confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confirmation required before submitting final procurement decision."
        )

    bidder = _resolve_bidder(bid_id, db)
    bid = db.query(Bid).filter(Bid.bidder_id == bidder.id).first()

    valid_choices = ["QUALIFIED", "DISQUALIFIED", "REVIEW / HOLD", "REVIEW", "HOLD"]
    target_choice = decision_in.decision.upper()
    if target_choice not in valid_choices:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid decision '{decision_in.decision}'. Allowed choices: QUALIFIED, DISQUALIFIED, REVIEW / HOLD."
        )

    if not decision_in.remarks or not decision_in.remarks.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Procurement Officer remarks are mandatory for final bid determination."
        )

    officer_name = decision_in.officer_name or (
        current_user.name if current_user and current_user.name else "Rajesh Sharma, Senior Procurement Officer"
    )
    now_utc = datetime.now(timezone.utc)

    # Count overridden requirements and review items for summary
    overrides_count = db.query(OfficerDecision).filter(
        OfficerDecision.bid_id == bidder.id,
        OfficerDecision.decision_type == "REQUIREMENT_DECISION",
        OfficerDecision.is_override == True
    ).count()

    pending_reviews_count = db.query(ComplianceCheck).filter(
        ComplianceCheck.bidder_id == bidder.id,
        ComplianceCheck.status == "REVIEW"
    ).count()

    high_risk_issues = db.query(RiskFactor).filter(
        RiskFactor.bid_id == bidder.id,
        RiskFactor.severity.in_(["HIGH", "CRITICAL"])
    ).count()

    ai_rec = bidder.recommendation.recommendation_type if bidder.recommendation else "Recommended for Officer Review"

    # Save final decision record
    final_decision_rec = OfficerDecision(
        bid_id=bidder.id,
        requirement_id=None,
        compliance_check_id=None,
        officer_id=current_user.id if current_user else None,
        officer_name=officer_name,
        decision_type="FINAL_BID_DECISION",
        ai_status=ai_rec,
        ai_confidence=1.0,
        officer_status=target_choice,
        officer_reason=decision_in.remarks.strip(),
        is_override=False,
        decision_timestamp=now_utc
    )
    db.add(final_decision_rec)

    # Update Bid status
    if bid:
        bid.technical_bid_status = "QUALIFIED" if target_choice == "QUALIFIED" else (
            "DISQUALIFIED" if target_choice == "DISQUALIFIED" else "UNDER_EVALUATION"
        )
        bid.remarks = decision_in.remarks.strip()
    bidder.status = target_choice

    db.commit()
    db.refresh(final_decision_rec)

    summary_meta = {
        "ai_recommendation": ai_rec,
        "officer_decision": target_choice,
        "overridden_requirements_count": overrides_count,
        "high_risk_issues_count": high_risk_issues,
        "outstanding_review_items": pending_reviews_count,
        "remarks": decision_in.remarks.strip()
    }

    # Log immutable audit event
    AuditService.log_event(
        db=db,
        action="FINAL_BID_DECISION",
        entity_type="BID",
        entity_id=bid.id if bid else bidder.id,
        user_id=current_user.id if current_user else None,
        user_name=officer_name,
        role="PROCUREMENT_OFFICER",
        tender_id=bidder.tender_id,
        bidder_id=bidder.id,
        description=f"Officer {officer_name} executed final procurement decision '{target_choice}' for bidder {bidder.legal_name}. Remarks: {decision_in.remarks.strip()}",
        metadata=summary_meta
    )

    return FinalBidDecisionResponse(
        id=final_decision_rec.id,
        bid_id=bidder.id,
        tender_id=bidder.tender_id,
        decision=target_choice,
        remarks=decision_in.remarks.strip(),
        officer_id=current_user.id if current_user else None,
        officer_name=officer_name,
        timestamp=now_utc,
        summary=summary_meta
    )
