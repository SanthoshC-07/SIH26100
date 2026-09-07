import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import ComplianceCheck, OfficerReview, Bidder, Bid, Tender, Requirement, User, Document
from app.schemas.schemas import OfficerReviewCreate, OfficerReviewResponse, ComplianceCheckResponse
from app.api.deps import (
    get_current_user, get_current_officer, require_role, require_any_role, verify_bidder_ownership
)
from app.audit.audit_service import AuditService
from app.scoring import ComplianceScorer, RiskEngine, RecommendationGenerator
from app.scoring.compliance_engine import ComplianceEngine

router = APIRouter(prefix="/compliance", tags=["Compliance & Hybrid Engine"])

def _serialize_evidence(ev_data: Any) -> str:
    if isinstance(ev_data, (list, dict)):
        return json.dumps(ev_data)
    return str(ev_data or "")

def _resolve_bidder(bid_id: str, db: Session) -> Bidder:
    """Helper to resolve a bidder record whether passed a Bid ID or a Bidder ID."""
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

@router.post("/run/{bid_id}")
def trigger_compliance_run(
    bid_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("PROCUREMENT_OFFICER"))
):
    """
    Executes full hybrid compliance engine for all requirements for a bid/bidder.
    Procurement Officer access strictly required.
    """
    return run_compliance_evaluation(bid_id, db, current_user=current_user)

def run_compliance_evaluation(bid_id: str, db: Session, current_user: Optional[User] = None):
    """
    Internal evaluation runner for all requirements for a bid/bidder.
    Evaluates rules, semantic similarity, and cross-document consistency.
    """
    bidder = _resolve_bidder(bid_id, db)
    tender = db.query(Tender).filter(Tender.id == bidder.tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Associated Tender record not found")

    requirements = db.query(Requirement).filter(Requirement.tender_id == tender.id).all()
    req_list = [
        {
            "id": r.id,
            "clause_number": r.clause_number,
            "category": r.category,
            "description": r.description,
            "mandatory": r.mandatory,
            "threshold": r.threshold,
            "threshold_unit": r.threshold_unit,
            "required_years": r.required_years,
            "time_period_years": r.required_years,
            "required_pipeline_length_km": r.required_pipeline_length_km,
            "required_diameter_inch": (r.conditions or {}).get("required_diameter_inch", 24.0) if isinstance(r.conditions, dict) else 24.0,
            "required_pipeline_type": r.required_pipeline_type,
            "required_manpower_count": r.required_manpower_count,
            "required_qualification": r.required_qualification,
            "required_sector": r.required_sector,
            "conditions": r.conditions or {}
        }
        for r in requirements
    ]

    # Gather extracted entities across bidder documents
    extracted_entities_list = []
    from app.documents.entity_extractor import EntityExtractor
    for d in bidder.documents:
        if d.entities:
            for ent in d.entities:
                extracted_entities_list.append({
                    "entity_type": ent.entity_type,
                    "entity_value": ent.entity_value,
                    "normalized_value": ent.normalized_value,
                    "confidence": ent.confidence,
                    "context_snippet": ent.context_snippet,
                    "page_number": ent.page_number,
                    "document_id": d.id,
                    "document_name": d.document_name
                })
        elif d.extracted_text:
            extracted_entities_list.extend(EntityExtractor.extract_all_entities(d.extracted_text, d.document_name, d.id))

    bidder_dict = {
        "id": bidder.id,
        "legal_name": bidder.legal_name,
        "bidder_name": bidder.bidder_name,
        "pan": bidder.pan,
        "gstin": bidder.gstin,
        "oil_gas_experience_years": bidder.oil_gas_experience_years,
        "pipeline_experience_years": bidder.pipeline_experience_years,
        "projects": [
            {
                "project_name": p.project_name,
                "client_name": p.client_name,
                "sector": p.sector,
                "pipeline_length_km": p.pipeline_length_km,
                "pipeline_diameter": p.pipeline_diameter,
                "project_value": p.project_value,
                "bidder_role": p.bidder_role,
                "scope_of_work": p.scope_of_work,
                "evidence_document_id": p.evidence_document_id
            }
            for p in bidder.projects
        ],
        "personnel": [
            {
                "name": pr.name,
                "designation": pr.designation,
                "qualification": pr.qualification,
                "years_of_experience": pr.years_of_experience,
                "pipeline_experience_years": pr.pipeline_experience_years,
                "document_id": pr.document_id
            }
            for pr in bidder.personnel
        ],
        "extracted_entities": extracted_entities_list
    }

    import re
    evidence_by_req = {}
    for r in requirements:
        req_id = r.id
        clause_no = (r.clause_number or "").upper()
        cat = (r.category or "").upper()
        
        matched_docs = []
        for d in bidder.documents:
            name_lower = d.document_name.lower()
            if clause_no and clause_no.lower() in name_lower:
                matched_docs.append(d)
                continue
            num_match = re.search(r"req-?0*(\d+)", clause_no, re.IGNORECASE)
            if num_match:
                prefix = f"{int(num_match.group(1)):02d}_"
                if prefix in name_lower or f"0{num_match.group(1)}_" in name_lower or f"req-0{num_match.group(1)}" in name_lower:
                    matched_docs.append(d)
                    continue
            if cat in ["GST", "GST_TAX_COMPLIANCE"] and "gst" in name_lower:
                matched_docs.append(d)
            elif cat in ["PAN", "INCOME_TAX_PAN"] and "pan" in name_lower:
                matched_docs.append(d)
            elif cat in ["FINANCIAL_TURNOVER", "FINANCIAL_ELIGIBILITY", "FINANCIAL", "TURNOVER"] and any(k in name_lower for k in ["financial", "turnover", "ca_cert", "audited"]):
                matched_docs.append(d)
            elif cat in ["SIMILAR_PIPELINE_EXPERIENCE", "SIMILAR_WORK", "SIMILAR_PIPELINE"] and any(k in name_lower for k in ["similar", "pipeline_exp", "pipeline_experience"]):
                matched_docs.append(d)
            elif cat in ["TECHNICAL_MANPOWER", "MANPOWER"] and any(k in name_lower for k in ["manpower", "personnel", "cv", "engineer"]):
                matched_docs.append(d)
            elif cat in ["OIL_GAS_EXPERIENCE", "EXPERIENCE_ELIGIBILITY"] and any(k in name_lower for k in ["oil_gas", "sector_exp", "experience_cert", "oil & gas"]):
                matched_docs.append(d)
            elif cat in ["HSE_SAFETY", "HSE", "SAFETY"] and any(k in name_lower for k in ["hse", "safety", "iso"]):
                matched_docs.append(d)

        matched_doc_ids = {d.id for d in matched_docs}
        if not matched_docs and len(bidder.documents) == 1:
            matched_docs = bidder.documents
            matched_doc_ids = {d.id for d in bidder.documents}

        req_entities = [e for e in extracted_entities_list if e.get("document_id") in matched_doc_ids]
        req_chunks = []
        for d in matched_docs:
            if d.extracted_text:
                for idx, chunk in enumerate(d.extracted_text.split("\n\n--- Page Break ---\n\n")):
                    req_chunks.append({
                        "document_id": d.id,
                        "document_name": d.document_name,
                        "page_number": idx + 1,
                        "text": chunk
                    })

        evidence_by_req[req_id] = {
            "entities": req_entities,
            "doc_chunks": req_chunks,
            "tender_number": tender.tender_number
        }
        if clause_no:
            evidence_by_req[clause_no] = evidence_by_req[req_id]

    eval_result = ComplianceEngine.evaluate_bidder(
        tender={"id": tender.id, "tender_number": tender.tender_number},
        bidder=bidder_dict,
        requirements=req_list,
        evidence_by_req=evidence_by_req
    )

    # Sync ComplianceCheck records to database
    from app.models.models import Evidence
    for check_data in eval_result["requirements"]:
        req_id = check_data["requirement_id"]
        existing_check = db.query(ComplianceCheck).filter(
            ComplianceCheck.bidder_id == bidder.id,
            ComplianceCheck.requirement_id == req_id
        ).first()

        if existing_check:
            existing_check.status = check_data["status"]
            existing_check.confidence = check_data["confidence"]
            existing_check.evidence_text = _serialize_evidence(check_data["evidence"])
            existing_check.reason = check_data["explanation"]
            existing_check.document_name = check_data["source_document"]
            existing_check.document_id = check_data.get("document_id")
            existing_check.page_number = check_data["page_number"]
            existing_check.verification_method = check_data["method"]
            existing_check.verification_source = check_data["source"]
            existing_check.rule_version = "v3.0.0-petroleum-hybrid"
            existing_check.verified_at = datetime.now(timezone.utc)
            
            # Clear old evidence and add fresh evidence item
            existing_check.evidence_items.clear()
            ev = Evidence(
                compliance_check_id=existing_check.id,
                document_id=check_data.get("document_id"),
                document_name=check_data.get("source_document"),
                page_number=check_data.get("page_number", 1),
                source_text=_serialize_evidence(check_data.get("source_text") or check_data.get("evidence")),
                extraction_method=check_data.get("method", "HYBRID_RULE_AND_NLP"),
                extracted_entities=check_data.get("extracted_entities", {}),
                calculation_breakdown=check_data.get("rule_result", {}) if isinstance(check_data.get("rule_result"), dict) else {"rule": check_data.get("rule_result")},
                confidence=check_data.get("confidence", 1.0)
            )
            db.add(ev)
        else:
            new_check = ComplianceCheck(
                bidder_id=bidder.id,
                requirement_id=req_id,
                status=check_data["status"],
                confidence=check_data["confidence"],
                score_contribution=1.0 if check_data["status"] == "PASS" else (0.5 if check_data["status"] == "REVIEW" else 0.0),
                evidence_text=_serialize_evidence(check_data["evidence"]),
                reason=check_data["explanation"],
                document_name=check_data["source_document"],
                document_id=check_data.get("document_id"),
                page_number=check_data["page_number"],
                verification_method=check_data["method"],
                verification_source=check_data["source"],
                rule_version="v3.0.0-petroleum-hybrid",
                verified_at=datetime.now(timezone.utc)
            )
            db.add(new_check)
            db.flush()
            
            ev = Evidence(
                compliance_check_id=new_check.id,
                document_id=check_data.get("document_id"),
                document_name=check_data.get("source_document"),
                page_number=check_data.get("page_number", 1),
                source_text=_serialize_evidence(check_data.get("source_text") or check_data.get("evidence")),
                extraction_method=check_data.get("method", "HYBRID_RULE_AND_NLP"),
                extracted_entities=check_data.get("extracted_entities", {}),
                calculation_breakdown=check_data.get("rule_result", {}) if isinstance(check_data.get("rule_result"), dict) else {"rule": check_data.get("rule_result")},
                confidence=check_data.get("confidence", 1.0)
            )
            db.add(ev)

    # Update bidder scores & recommendation
    if bidder.compliance_score:
        bidder.compliance_score.overall_score = eval_result["compliance_score"]
        bidder.compliance_score.statutory_score = eval_result["score_breakdown"]["statutory_score"]
        bidder.compliance_score.financial_score = eval_result["score_breakdown"]["financial_score"]
        bidder.compliance_score.tender_specific_score = eval_result["score_breakdown"]["tender_specific_score"]
    
    if bidder.risk_assessment:
        bidder.risk_assessment.risk_level = eval_result["risk_assessment"]["risk_level"]
        bidder.risk_assessment.primary_risk_factors = eval_result["risk_assessment"]["primary_risk_factors"]
        bidder.risk_assessment.risk_score = eval_result["risk_assessment"]["risk_score"]

    if bidder.recommendation:
        bidder.recommendation.recommendation_type = eval_result["recommendation"]["recommendation_type"]
        bidder.recommendation.summary = eval_result["recommendation"]["summary"]
        bidder.recommendation.detailed_reasons = eval_result["recommendation"]["detailed_reasons"]

    bidder.status = eval_result["overall_status"]

    # Persist risk factors to SQLite
    RiskEngine.persist_risk_factors(db, bidder.id, eval_result["risk_assessment"])

    # Record historical VerificationRun in SQLite
    from app.models.models import VerificationRun
    run_entry = VerificationRun(
        bid_id=bidder.id,
        tender_id=tender.id,
        triggered_by="PROCUREMENT_OFFICER",
        status="COMPLETED",
        total_requirements=eval_result["summary_counts"]["total"],
        pass_count=eval_result["summary_counts"]["pass"],
        fail_count=eval_result["summary_counts"]["fail"],
        review_count=eval_result["summary_counts"]["review"],
        insufficient_count=eval_result["summary_counts"]["insufficient"],
        not_applicable_count=eval_result["summary_counts"]["not_applicable"],
        compliance_score=eval_result["compliance_score"],
        compliance_percentage=eval_result["compliance_percentage"],
        risk_level=eval_result["risk_assessment"]["risk_level"],
        recommendation=eval_result["recommendation"]["recommendation_type"],
        run_metadata={"overall_status": eval_result["overall_status"]}
    )
    db.add(run_entry)
    db.commit()

    # Log COMPLIANCE_RUN audit event
    AuditService.log_event(
        db=db,
        action="COMPLIANCE_RUN",
        entity_type="BID",
        entity_id=bidder.id,
        user_name="PROCUREMENT_OFFICER",
        role="PROCUREMENT_OFFICER",
        tender_id=tender.id,
        bidder_id=bidder.id,
        description=f"Automated compliance evaluation executed for {bidder.legal_name}. Score: {eval_result['compliance_score']}%, Risk: {eval_result['risk_assessment']['risk_level']}",
        metadata={"compliance_score": eval_result["compliance_score"], "risk_level": eval_result["risk_assessment"]["risk_level"]}
    )

    return eval_result

@router.get("/{bid_id}")
def get_compliance_dossier(bid_id: str, db: Session = Depends(get_db)):
    """
    Returns complete compliance evaluation results with score, risk, and summary.
    """
    return run_compliance_evaluation(bid_id, db)

@router.get("/{bid_id}/requirements")
def get_bid_compliance_requirements(bid_id: str, db: Session = Depends(get_db)):
    """
    Returns list of requirement compliance results for a given bid/bidder.
    """
    eval_res = run_compliance_evaluation(bid_id, db)
    return eval_res.get("requirements", [])

@router.get("/{bid_id}/requirements/{requirement_id}")
def get_single_requirement_compliance(bid_id: str, requirement_id: str, db: Session = Depends(get_db)):
    """
    Returns detailed compliance result for a specific requirement clause.
    """
    bidder = _resolve_bidder(bid_id, db)
    req = db.query(Requirement).filter(Requirement.id == requirement_id).first()
    if not req:
        # Also try match by clause_number or category
        req = db.query(Requirement).filter(
            Requirement.tender_id == bidder.tender_id,
            (Requirement.clause_number == requirement_id) | (Requirement.category == requirement_id)
        ).first()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement clause not found")

    check = db.query(ComplianceCheck).filter(
        ComplianceCheck.bidder_id == bidder.id,
        ComplianceCheck.requirement_id == req.id
    ).first()

    if not check:
        eval_res = run_compliance_evaluation(bid_id, db)
        for r in eval_res.get("requirements", []):
            if r.get("requirement_id") == req.id:
                return r

    if not check:
        raise HTTPException(status_code=404, detail="Compliance check record not found")

    first_ev = check.evidence_items[0] if check.evidence_items else None
    return {
        "requirement_id": req.id,
        "clause_number": req.clause_number,
        "category": req.category,
        "description": req.description,
        "mandatory": req.mandatory,
        "status": check.status,
        "confidence": check.confidence,
        "evidence": check.evidence_text,
        "source_document": check.document_name or "Evidence_Document.pdf",
        "document_name": check.document_name,
        "document_id": check.document_id,
        "page_number": check.page_number,
        "source_text": check.evidence_text,
        "extracted_entities": first_ev.extracted_entities if first_ev else {},
        "rule_result": first_ev.calculation_breakdown if first_ev else {},
        "semantic_score": 1.0,
        "explanation": check.reason,
        "reason": check.reason,
        "verified_at": check.verified_at
    }

@router.post("/{bid_id}/requirements/{requirement_id}/verify")
@router.post("/{bid_id}/requirements/{requirement_id}/reverify")
def verify_single_requirement(
    bid_id: str,
    requirement_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("PROCUREMENT_OFFICER"))
):
    """
    Re-runs single requirement verification for a bid/bidder.
    """
    bidder = _resolve_bidder(bid_id, db)
    req = db.query(Requirement).filter(Requirement.id == requirement_id).first()
    if not req:
        req = db.query(Requirement).filter(
            Requirement.tender_id == bidder.tender_id,
            (Requirement.clause_number == requirement_id) | (Requirement.category == requirement_id)
        ).first()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement clause not found")

    # Fetch document entities
    extracted_entities_list = []
    from app.documents.entity_extractor import EntityExtractor
    for d in bidder.documents:
        if d.entities:
            for ent in d.entities:
                extracted_entities_list.append({
                    "entity_type": ent.entity_type,
                    "entity_value": ent.entity_value,
                    "normalized_value": ent.normalized_value,
                    "confidence": ent.confidence,
                    "context_snippet": ent.context_snippet,
                    "page_number": ent.page_number,
                    "document_id": d.id,
                    "document_name": d.document_name
                })
        elif d.extracted_text:
            extracted_entities_list.extend(EntityExtractor.extract_all_entities(d.extracted_text, d.document_name, d.id))

    bidder_dict = {
        "id": bidder.id,
        "legal_name": bidder.legal_name,
        "bidder_name": bidder.bidder_name,
        "pan": bidder.pan,
        "gstin": bidder.gstin,
        "oil_gas_experience_years": bidder.oil_gas_experience_years,
        "pipeline_experience_years": bidder.pipeline_experience_years,
        "projects": [
            {
                "project_name": p.project_name,
                "client_name": p.client_name,
                "sector": p.sector,
                "pipeline_length_km": p.pipeline_length_km,
                "pipeline_diameter": p.pipeline_diameter,
                "project_value": p.project_value,
                "bidder_role": p.bidder_role,
                "scope_of_work": p.scope_of_work,
                "evidence_document_id": p.evidence_document_id
            }
            for p in bidder.projects
        ],
        "personnel": [
            {
                "name": pr.name,
                "designation": pr.designation,
                "qualification": pr.qualification,
                "years_of_experience": pr.years_of_experience,
                "pipeline_experience_years": pr.pipeline_experience_years,
                "document_id": pr.document_id
            }
            for pr in bidder.personnel
        ],
        "extracted_entities": extracted_entities_list
    }

    req_dict = {
        "id": req.id,
        "clause_number": req.clause_number,
        "category": req.category,
        "description": req.description,
        "mandatory": req.mandatory,
        "threshold": req.threshold,
        "threshold_unit": req.threshold_unit
    }

    res = ComplianceEngine.verify_requirement(
        requirement=req_dict,
        evidence={"entities": extracted_entities_list},
        bidder=bidder_dict
    )

    from app.models.models import Evidence
    # Save to database
    existing_check = db.query(ComplianceCheck).filter(
        ComplianceCheck.bidder_id == bidder.id,
        ComplianceCheck.requirement_id == req.id
    ).first()

    if existing_check:
        existing_check.status = res["status"]
        existing_check.confidence = res["confidence"]
        existing_check.evidence_text = _serialize_evidence(res.get("evidence"))
        existing_check.reason = res["explanation"]
        existing_check.document_name = res["source_document"]
        existing_check.page_number = res["page_number"]
        existing_check.verified_at = datetime.now(timezone.utc)
        
        existing_check.evidence_items.clear()
        ev = Evidence(
            compliance_check_id=existing_check.id,
            document_id=res.get("document_id"),
            document_name=res.get("source_document"),
            page_number=res.get("page_number", 1),
            source_text=_serialize_evidence(res.get("source_text") or res.get("evidence")),
            extraction_method=res.get("method", "HYBRID_RULE_AND_NLP"),
            extracted_entities=res.get("extracted_entities", {}),
            calculation_breakdown=res.get("rule_result", {}) if isinstance(res.get("rule_result"), dict) else {"rule": res.get("rule_result")},
            confidence=res.get("confidence", 1.0)
        )
        db.add(ev)
    else:
        new_check = ComplianceCheck(
            bidder_id=bidder.id,
            requirement_id=req.id,
            status=res["status"],
            confidence=res["confidence"],
            score_contribution=1.0 if res["status"] == "PASS" else 0.0,
            evidence_text=_serialize_evidence(res.get("evidence")),
            reason=res["explanation"],
            document_name=res["source_document"],
            page_number=res["page_number"],
            verification_method=res["method"],
            verification_source=res["source"],
            rule_version="v3.0.0-petroleum-hybrid",
            verified_at=datetime.now(timezone.utc)
        )
        db.add(new_check)
        db.flush()
        
        ev = Evidence(
            compliance_check_id=new_check.id,
            document_id=res.get("document_id"),
            document_name=res.get("source_document"),
            page_number=res.get("page_number", 1),
            source_text=_serialize_evidence(res.get("source_text") or res.get("evidence")),
            extraction_method=res.get("method", "HYBRID_RULE_AND_NLP"),
            extracted_entities=res.get("extracted_entities", {}),
            calculation_breakdown=res.get("rule_result", {}) if isinstance(res.get("rule_result"), dict) else {"rule": res.get("rule_result")},
            confidence=res.get("confidence", 1.0)
        )
        db.add(ev)
    db.commit()

    AuditService.log_event(
        db=db,
        action="COMPLIANCE_REVERIFIED",
        entity_type="REQUIREMENT",
        entity_id=req.id,
        user_name="PROCUREMENT_OFFICER",
        role="PROCUREMENT_OFFICER",
        tender_id=bidder.tender_id,
        bidder_id=bidder.id,
        description=f"Single requirement {req.category} reverified for bidder {bidder.legal_name}. Result: {res['status']}",
        metadata={"status": res["status"], "confidence": res["confidence"]}
    )

    return res

@router.get("/{bid_id}/summary")
def get_compliance_summary(
    bid_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns high-level compliance summary, category counts, and overall mandatory status.
    """
    bidder = _resolve_bidder(bid_id, db)
    verify_bidder_ownership(bidder.id, current_user, db)
    eval_res = run_compliance_evaluation(bid_id, db)
    return {
        "bidder_id": eval_res["bidder_id"],
        "bidder_name": eval_res["bidder_name"],
        "tender_number": eval_res["tender_number"],
        "overall_status": eval_res["overall_status"],
        "status_summary": eval_res["status_summary"],
        "compliance_score": eval_res["compliance_score"],
        "risk_level": eval_res["risk_assessment"]["risk_level"],
        "summary_counts": eval_res["summary_counts"],
        "cross_document_consistency": eval_res["cross_document_consistency"]["status"],
        "recommendation": eval_res["recommendation"]["recommendation_type"]
    }

@router.post("/review", response_model=OfficerReviewResponse)
@router.post("/{check_id}/review", response_model=OfficerReviewResponse)
@router.post("/{bid_id}/requirements/{requirement_id}/override", response_model=OfficerReviewResponse)
def review_compliance_check(
    review_in: OfficerReviewCreate,
    check_id: Optional[str] = None,
    bid_id: Optional[str] = None,
    requirement_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("PROCUREMENT_OFFICER"))
):
    if not review_in.bidder_id and bid_id:
        review_in.bidder_id = bid_id
    if not review_in.requirement_id and requirement_id:
        review_in.requirement_id = requirement_id
    check = None
    if check_id and check_id not in ("undefined", "null", ""):
        check = db.query(ComplianceCheck).filter(ComplianceCheck.id == check_id).first()
        if not check:
            check = db.query(ComplianceCheck).filter(ComplianceCheck.requirement_id == check_id).first()

    # Search by requirement_id if check still not resolved
    if not check and review_in.requirement_id:
        req = db.query(Requirement).filter(
            (Requirement.id == review_in.requirement_id) |
            (Requirement.clause_number == review_in.requirement_id) |
            (Requirement.category == review_in.requirement_id)
        ).first()

        if req and review_in.bidder_id:
            check = db.query(ComplianceCheck).filter(
                ComplianceCheck.bidder_id == review_in.bidder_id,
                ComplianceCheck.requirement_id == req.id
            ).first()
            if not check:
                check = ComplianceCheck(
                    bidder_id=review_in.bidder_id,
                    requirement_id=req.id,
                    status=review_in.new_status,
                    confidence=0.95,
                    score_contribution=1.0 if review_in.new_status == "PASS" else (0.5 if review_in.new_status == "REVIEW" else 0.0),
                    reason=review_in.remarks,
                    verification_source="OFFICER_DETERMINATION",
                    verification_method="MANUAL_OFFICER_REVIEW",
                    verified_at=datetime.now(timezone.utc)
                )
                db.add(check)
                db.flush()
        elif req:
            check = db.query(ComplianceCheck).filter(ComplianceCheck.requirement_id == req.id).first()

    if not check and review_in.bidder_id:
        check = db.query(ComplianceCheck).filter(ComplianceCheck.bidder_id == review_in.bidder_id).first()

    if not check:
        raise HTTPException(status_code=404, detail="Compliance check record not found for review determination.")

    bidder = db.query(Bidder).filter(Bidder.id == check.bidder_id).first()
    if not bidder:
        raise HTTPException(status_code=404, detail="Associated bidder record not found.")

    if not review_in.remarks or not review_in.remarks.strip():
        raise HTTPException(
            status_code=400,
            detail="Officer override reason is mandatory. AI compliance determination cannot be overridden without documented justification."
        )

    prev_status = check.status
    prev_reason = check.reason or "Initial AI Evaluation"
    action_type = review_in.action_type or "OFFICER_OVERRIDE"
    
    # Update check status based on officer decision while preserving baseline AI reason
    check.status = review_in.new_status
    check.score_contribution = 1.0 if review_in.new_status == "PASS" else (0.5 if review_in.new_status == "REVIEW" else 0.0)
    check.reason = f"[OFFICER {action_type}]: {review_in.remarks.strip()} (Original AI Baseline Status: {prev_status} | Note: {prev_reason})"
    check.verified_at = datetime.now(timezone.utc)
    
    officer_name = current_user.name if hasattr(current_user, 'name') and current_user.name else getattr(current_user, 'full_name', 'Rajesh Sharma, Senior Procurement Officer')

    # Save Officer Review record
    review = OfficerReview(
        bidder_id=bidder.id,
        requirement_id=check.requirement_id,
        officer_id=current_user.id,
        officer_name=officer_name,
        previous_status=prev_status,
        new_status=review_in.new_status,
        action_type=action_type,
        remarks=review_in.remarks.strip(),
        reviewed_at=datetime.now(timezone.utc)
    )
    db.add(review)

    # Save Officer Override record for full Phase 4 traceability
    from app.models.models import OfficerOverride
    override_rec = OfficerOverride(
        bid_id=bidder.id,
        requirement_id=check.requirement_id,
        compliance_check_id=check.id,
        officer_id=current_user.id,
        officer_name=officer_name,
        original_ai_status=prev_status,
        overridden_status=review_in.new_status,
        override_reason=review_in.remarks.strip(),
        action_type=action_type,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(override_rec)

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
        bidder.bidder_name or bidder.legal_name, checks_list, score_data["overall_score"], risk_data["risk_level"]
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
        action=f"OFFICER_{action_type}",
        entity_type="COMPLIANCE_CHECK",
        entity_id=check.id,
        user_id=current_user.id,
        user_name=officer_name,
        tender_id=bidder.tender_id,
        bidder_id=bidder.id,
        previous_state={"status": prev_status},
        new_state={"status": review_in.new_status, "remarks": review_in.remarks},
        reason=review_in.remarks
    )

    return review

@router.get("/reviews/pending", response_model=List[ComplianceCheckResponse])
def get_pending_review_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role("PROCUREMENT_OFFICER", "ADMIN"))
):
    pending = db.query(ComplianceCheck).filter(ComplianceCheck.status == "REVIEW").all()
    results = []
    for c in pending:
        results.append({
            "id": c.id,
            "bidder_id": c.bidder_id,
            "requirement_id": c.requirement_id,
            "clause_number": c.clause_number,
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
