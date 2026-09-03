from typing import Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.models import (
    Bidder, Tender, Requirement, Document, ExtractedEntity,
    ComplianceCheck, Evidence, ComplianceScore, RiskAssessment,
    Recommendation, PortalVerification, BidderProject, BidderPersonnel
)
from app.checkers import get_checker_for_category
from app.rules import CrossDocumentConsistencyEngine
from app.scoring import ComplianceScorer, RiskEngine, RecommendationGenerator
from app.audit import AuditService
from app.core.logging_config import logger

class ComplianceEngine:
    @staticmethod
    def run_full_verification(db: Session, bidder_id: str, officer_id: str = None, officer_name: str = "SYSTEM") -> Dict[str, Any]:
        bidder = db.query(Bidder).filter(Bidder.id == bidder_id).first()
        if not bidder:
            raise ValueError(f"Bidder with id {bidder_id} not found")

        tender = db.query(Tender).filter(Tender.id == bidder.tender_id).first()
        if not tender:
            raise ValueError(f"Tender with id {bidder.tender_id} not found")

        requirements = db.query(Requirement).filter(Requirement.tender_id == tender.id).all()
        documents = db.query(Document).filter(Document.bidder_id == bidder_id).all()
        db_projects = db.query(BidderProject).filter(BidderProject.bidder_id == bidder_id).all()
        db_personnel = db.query(BidderPersonnel).filter(BidderPersonnel.bidder_id == bidder_id).all()

        # Collect all extracted entities
        doc_ids = [d.id for d in documents]
        all_entities = db.query(ExtractedEntity).filter(ExtractedEntity.document_id.in_(doc_ids)).all() if doc_ids else []
        
        entities_data = []
        for e in all_entities:
            doc = next((d for d in documents if d.id == e.document_id), None)
            entities_data.append({
                "entity_type": e.entity_type,
                "entity_value": e.entity_value,
                "normalized_value": e.normalized_value,
                "confidence": e.confidence,
                "page_number": e.page_number,
                "context_snippet": e.context_snippet,
                "document_id": e.document_id,
                "document_name": doc.document_name if doc else "Document.pdf"
            })

        # Build document text chunks for semantic fallback
        doc_chunks = []
        for d in documents:
            if d.extracted_text:
                for idx, chunk in enumerate(d.extracted_text.split("\n\n--- Page Break ---\n\n")):
                    doc_chunks.append({
                        "document_id": d.id,
                        "document_name": d.document_name,
                        "page_number": idx + 1,
                        "text": chunk
                    })

        # Structured Bidder Context
        bidder_context = {
            "id": bidder.id,
            "legal_name": bidder.legal_name,
            "bidder_name": bidder.legal_name,
            "trade_name": bidder.trade_name,
            "pan": bidder.pan,
            "gstin": bidder.gstin,
            "udyam_number": bidder.udyam_number,
            "projects": [
                {
                    "project_name": p.project_name,
                    "client_name": p.client_name,
                    "sector": p.sector,
                    "pipeline_type": p.pipeline_type,
                    "pipeline_length_km": p.pipeline_length_km,
                    "pipeline_diameter": p.pipeline_diameter,
                    "project_value": p.project_value,
                    "scope_of_work": p.scope_of_work,
                    "bidder_role": p.bidder_role,
                    "evidence_document_id": p.evidence_document_id
                } for p in db_projects
            ],
            "personnel": [
                {
                    "name": pers.name,
                    "designation": pers.designation,
                    "qualification": pers.qualification,
                    "specialization": pers.specialization,
                    "years_of_experience": pers.years_of_experience,
                    "pipeline_experience_years": pers.pipeline_experience_years,
                    "document_id": pers.document_id
                } for pers in db_personnel
            ]
        }

        # Clear existing compliance checks for re-run
        db.query(ComplianceCheck).filter(ComplianceCheck.bidder_id == bidder_id).delete()
        if bidder.compliance_score:
            db.delete(bidder.compliance_score)
        if bidder.risk_assessment:
            db.delete(bidder.risk_assessment)
        if bidder.recommendation:
            db.delete(bidder.recommendation)
        db.commit()

        checks_created = []

        for req in requirements:
            cat = (req.category or "OTHER").upper()
            mandatory = req.mandatory

            req_dict = {
                "id": req.id,
                "category": cat,
                "description": req.description,
                "threshold": req.threshold,
                "threshold_unit": req.threshold_unit,
                "required_pipeline_length_km": req.required_pipeline_length_km,
                "required_manpower_count": req.required_manpower_count,
                "required_years": req.required_years,
                "mandatory": mandatory
            }

            evidence_context = {
                "entities": entities_data,
                "doc_chunks": doc_chunks,
                "tender_number": tender.tender_number
            }

            # Dispatch to appropriate Checker
            checker = get_checker_for_category(cat)
            result = checker.verify(req_dict, bidder_context, evidence_context)

            # Create ComplianceCheck record
            check_record = ComplianceCheck(
                bidder_id=bidder.id,
                requirement_id=req.id,
                status=result.get("status", "REVIEW"),
                confidence=result.get("confidence", 1.0),
                score_contribution=1.0 if result.get("status") == "PASS" else (0.5 if result.get("status") == "REVIEW" else 0.0),
                reason=result.get("reason", ""),
                evidence_text=result.get("evidence", ""),
                document_id=result.get("document_id"),
                document_name=result.get("document_name"),
                page_number=result.get("page_number", 1),
                verification_source=result.get("source", "RULE_ENGINE"),
                verification_method=result.get("method", "DETERMINISTIC_RULE"),
                rule_version=req.rule_version or "2.0",
                verified_at=datetime.now(timezone.utc)
            )
            db.add(check_record)
            db.flush()

            # Create associated Evidence item
            ev_record = Evidence(
                compliance_check_id=check_record.id,
                document_id=result.get("document_id"),
                document_name=result.get("document_name"),
                page_number=result.get("page_number", 1),
                source_text=result.get("evidence", result.get("reason", "")),
                extraction_method="PDF_TEXT",
                extracted_entities=result.get("verification_details", {}),
                confidence=result.get("confidence", 1.0),
                calculation_breakdown=result.get("verification_details"),
                verified_source=result.get("source", "DEMO / MOCK GOVERNMENT SOURCE")
            )
            db.add(ev_record)

            checks_created.append({
                "requirement_category": cat,
                "requirement_mandatory": mandatory,
                "status": check_record.status,
                "confidence": check_record.confidence,
                "reason": check_record.reason
            })

        # Cross-document consistency check
        consistency_res = CrossDocumentConsistencyEngine.evaluate(
            bidder.legal_name, bidder.gstin, bidder.pan, entities_data
        )
        if consistency_res["status"] == "REVIEW":
            for c in checks_created:
                if c["requirement_category"] in ["GST", "PAN"]:
                    c["confidence"] = min(c["confidence"], 0.82)

        # 4. Scoring & Risk
        score_data = ComplianceScorer.calculate_score(checks_created)
        risk_data = RiskEngine.assess_risk(checks_created, score_data["overall_score"])
        rec_data = RecommendationGenerator.generate_recommendation(
            bidder.legal_name, checks_created, score_data["overall_score"], risk_data["risk_level"]
        )

        # Persist score
        comp_score = ComplianceScore(
            bidder_id=bidder.id,
            overall_score=score_data["overall_score"],
            statutory_score=score_data["statutory_score"],
            financial_score=score_data["financial_score"],
            tender_specific_score=score_data["tender_specific_score"],
            documentation_score=score_data["documentation_score"],
            other_score=score_data["other_score"],
            weights_applied=score_data["weights_applied"]
        )
        db.add(comp_score)

        # Persist risk
        risk_record = RiskAssessment(
            bidder_id=bidder.id,
            risk_level=risk_data["risk_level"],
            primary_risk_factors=risk_data["primary_risk_factors"],
            risk_score=risk_data["risk_score"]
        )
        db.add(risk_record)

        # Persist recommendation
        rec_record = Recommendation(
            bidder_id=bidder.id,
            recommendation_type=rec_data["recommendation_type"],
            summary=rec_data["summary"],
            detailed_reasons=rec_data["detailed_reasons"]
        )
        db.add(rec_record)

        # Update bidder status
        bidder.status = "UNDER_REVIEW" if risk_data["risk_level"] in ["HIGH", "CRITICAL", "MEDIUM"] else "VERIFIED"
        db.commit()

        # Audit log
        AuditService.log_action(
            db=db,
            action="BIDDER_VERIFIED",
            entity_type="BIDDER",
            entity_id=bidder.id,
            user_id=officer_id,
            user_name=officer_name,
            tender_id=tender.id,
            bidder_id=bidder.id,
            new_state={
                "compliance_score": score_data["overall_score"],
                "risk_level": risk_data["risk_level"],
                "recommendation": rec_data["recommendation_type"]
            },
            reason=f"Automated 7-Core compliance verification executed for {bidder.legal_name} (MoPNG Pipeline Cell)."
        )

        return {
            "bidder_id": bidder.id,
            "status": bidder.status,
            "score": score_data,
            "risk": risk_data,
            "recommendation": rec_data
        }
