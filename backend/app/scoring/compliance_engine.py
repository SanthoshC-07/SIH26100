from typing import Dict, Any, List, Optional
from app.checkers import get_checker_for_category
from app.rules.cross_document_rule import CrossDocumentConsistencyEngine
from app.scoring.confidence_engine import ConfidenceEngine
from app.scoring.compliance_scorer import ComplianceScorer
from app.scoring.risk_engine import RiskEngine
from app.scoring.recommendation_generator import RecommendationGenerator

class ComplianceEngine:
    """
    SIH26100 Phase 3: Petroleum-Specific Hybrid Compliance Engine
    Orchestrates deterministic rule verification, semantic NLP signals,
    cross-document consistency checks, and multi-signal confidence gating.
    """

    @classmethod
    def verify_requirement(
        cls,
        requirement: Dict[str, Any],
        evidence: Dict[str, Any],
        bidder: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes hybrid verification for a single tender requirement clause.
        """
        category = requirement.get("category") or "TENDER_SPECIFIC"
        checker = get_checker_for_category(category)
        
        # Execute specialized domain checker
        raw_result = checker.verify(requirement, evidence, bidder)
        
        # Extract signals
        status = raw_result.get("status", "REVIEW")
        confidence = float(raw_result.get("confidence", 0.90))
        semantic_score = float(raw_result.get("semantic_score", 1.0)) if raw_result.get("semantic_score") is not None else None
        mandatory = requirement.get("mandatory", True)
        
        # Apply confidence gate
        has_missing = status == "INSUFFICIENT" or not raw_result.get("evidence")
        gated = ConfidenceEngine.apply_confidence_policy(
            provisional_status=status,
            overall_confidence=confidence,
            semantic_score=semantic_score if category in ["SIMILAR_PIPELINE_EXPERIENCE", "OIL_GAS_EXPERIENCE", "EXPERIENCE_ELIGIBILITY"] else None,
            has_missing_evidence=has_missing,
            has_contradictions=False,
            is_mandatory=mandatory
        )
        
        final_status = gated["status"]
        final_confidence = gated["confidence"]
        
        explanation = raw_result.get("explanation") or raw_result.get("reason") or "Requirement evaluated per MoPNG pipeline procurement specifications."
        
        # Convert evidence to list if string or dictionary
        raw_evidence = raw_result.get("evidence")
        if isinstance(raw_evidence, list):
            evidence_list = raw_evidence
        elif raw_evidence:
            evidence_list = [
                {
                    "document_name": raw_result.get("source_document") or raw_result.get("document_name") or "Evidence_Document.pdf",
                    "document_id": raw_result.get("document_id"),
                    "page_number": raw_result.get("page_number", 1),
                    "text": str(raw_evidence),
                    "extraction_method": raw_result.get("method", "PDF_TEXT")
                }
            ]
        else:
            evidence_list = []

        # Convert rule_results to list if dict
        raw_rules = raw_result.get("rule_results") or raw_result.get("rule_result")
        if isinstance(raw_rules, list):
            rule_results_list = raw_rules
        elif isinstance(raw_rules, dict):
            rule_results_list = [raw_rules]
        elif raw_rules:
            rule_results_list = [{"rule": "Evaluation Rule", "condition": str(raw_rules), "passed": final_status == "PASS"}]
        else:
            rule_results_list = []

        risk_val = raw_result.get("risk")
        if not risk_val:
            if final_status == "FAIL":
                risk_val = "HIGH" if mandatory else "MEDIUM"
            elif final_status in ["REVIEW", "INSUFFICIENT"]:
                risk_val = "MEDIUM"
            else:
                risk_val = "LOW"

        return {
            "requirement_id": requirement.get("id") or requirement.get("clause_number") or "REQ-UNSPECIFIED",
            "clause_number": requirement.get("clause_number"),
            "category": category,
            "requirement": requirement.get("description") or "",
            "description": requirement.get("description", ""),
            "mandatory": mandatory,
            "status": final_status,
            "confidence": round(final_confidence, 2),
            "confidence_gate": gated["gate"],
            "extracted_requirement": raw_result.get("extracted_requirement") or {"category": category, "threshold": requirement.get("threshold"), "mandatory": mandatory},
            "evidence": evidence_list,
            "rule_results": rule_results_list,
            "semantic_score": round(semantic_score, 2) if semantic_score is not None else None,
            "cross_document_consistency": raw_result.get("cross_document_consistency"),
            "explanation": explanation,
            "reason": explanation,
            "risk": risk_val,

            # Backwards compatibility fields for existing UI/API consumers
            "source_document": raw_result.get("source_document") or raw_result.get("document_name") or "Evidence_Document.pdf",
            "document_name": raw_result.get("document_name") or raw_result.get("source_document") or "Evidence_Document.pdf",
            "document_id": raw_result.get("document_id"),
            "page_number": raw_result.get("page_number", 1),
            "source_text": raw_result.get("source_text") or (evidence_list[0]["text"] if evidence_list else ""),
            "extracted_entities": raw_result.get("extracted_entities", {}),
            "rule_result": raw_result.get("rule_result", {}),
            "source": raw_result.get("source", "COMPLIANCE_ENGINE"),
            "method": raw_result.get("method", "HYBRID_RULE_AND_NLP"),
            "verification_details": raw_result.get("verification_details", {})
        }

    @classmethod
    def evaluate_bidder(
        cls,
        tender: Dict[str, Any],
        bidder: Dict[str, Any],
        requirements: List[Dict[str, Any]],
        evidence_by_req: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Executes the full compliance suite across all 7 core checks for a bidder.
        Enforces strict mandatory failure policy (failures are never hidden by average scores).
        """
        evidence_by_req = evidence_by_req or {}
        requirement_results = []
        bidder_name = bidder.get("legal_name") or bidder.get("bidder_name", "")
        claimed_gstin = bidder.get("gstin", "")
        claimed_pan = bidder.get("pan", "")
        
        # 1. Run all requirement checks
        all_extracted_entities = []
        for req in requirements:
            req_id = req.get("id") or req.get("clause_number") or req.get("category")
            req_evidence = evidence_by_req.get(req_id) or evidence_by_req.get(req.get("category")) or {}
            
            # Combine entities from bidder if not passed in evidence
            if not req_evidence.get("entities") and bidder.get("extracted_entities"):
                req_evidence["entities"] = bidder.get("extracted_entities")
            
            all_extracted_entities.extend(req_evidence.get("entities", []))
            
            check_res = cls.verify_requirement(req, req_evidence, bidder)
            requirement_results.append(check_res)

        # 2. Cross-document consistency verification
        consistency_res = CrossDocumentConsistencyEngine.evaluate(
            bidder_name=bidder_name,
            claimed_gstin=claimed_gstin,
            claimed_pan=claimed_pan,
            extracted_entities=all_extracted_entities
        )

        # 3. Aggregate Mandatory Overall Compliance Status
        mandatory_checks = [c for c in requirement_results if c.get("mandatory", True)]
        
        has_mandatory_fail = any(c.get("status") == "FAIL" for c in mandatory_checks)
        has_mandatory_review = any(c.get("status") == "REVIEW" for c in mandatory_checks)
        has_mandatory_insufficient = any(c.get("status") == "INSUFFICIENT" for c in mandatory_checks)
        all_mandatory_pass = all(c.get("status") in ["PASS", "NOT_APPLICABLE"] for c in mandatory_checks)
        
        if has_mandatory_fail:
            overall_status = "NON_COMPLIANT"
            status_summary = "NON-COMPLIANT: One or more mandatory statutory/technical requirements failed."
        elif has_mandatory_insufficient:
            overall_status = "INSUFFICIENT_EVIDENCE"
            status_summary = "INSUFFICIENT EVIDENCE: Mandatory compliance documentation is missing."
        elif has_mandatory_review:
            overall_status = "REVIEW_REQUIRED"
            status_summary = "REVIEW REQUIRED: Ambiguous technical evidence requires Procurement Officer determination."
        elif all_mandatory_pass:
            overall_status = "COMPLIANT"
            status_summary = "COMPLIANT: All mandatory petroleum procurement criteria fully satisfied."
        else:
            overall_status = "REVIEW_REQUIRED"
            status_summary = "UNDER EVALUATION: Requires officer confirmation."

        # 4. Compute weighted scores and risk rating
        score_input = [
            {
                "requirement_category": c.get("category"),
                "status": c.get("status"),
                "confidence": c.get("confidence", 0.95),
                "reason": c.get("explanation", "")
            }
            for c in requirement_results
        ]
        
        score_data = ComplianceScorer.calculate_score(score_input)
        risk_data = RiskEngine.assess_risk(score_input, score_data["overall_score"])
        rec_data = RecommendationGenerator.generate_recommendation(
            bidder_name, score_input, score_data["overall_score"], risk_data["risk_level"]
        )

        # Build comprehensive explainability breakdown
        total_count = len(requirement_results)
        pass_count = sum(1 for c in requirement_results if c.get("status") == "PASS")
        fail_count = sum(1 for c in requirement_results if c.get("status") == "FAIL")
        review_count = sum(1 for c in requirement_results if c.get("status") == "REVIEW")
        insufficient_count = sum(1 for c in requirement_results if c.get("status") == "INSUFFICIENT")
        na_count = sum(1 for c in requirement_results if c.get("status") == "NOT_APPLICABLE")
        critical_failures = sum(1 for c in mandatory_checks if c.get("status") == "FAIL")
        compliance_pct = round((pass_count / total_count * 100.0) if total_count > 0 else 0.0, 1)

        return {
            "bidder_id": bidder.get("id"),
            "bidder_name": bidder_name,
            "tender_id": tender.get("id"),
            "tender_number": tender.get("tender_number"),
            "overall_status": overall_status,
            "status_summary": status_summary,
            "mandatory_compliance": not (has_mandatory_fail or has_mandatory_insufficient),
            "compliance_score": score_data["overall_score"],
            "compliance_percentage": compliance_pct,
            "critical_failures": critical_failures,
            "overall_risk": risk_data["risk_level"],
            "score_breakdown": score_data,
            "risk_assessment": risk_data,
            "recommendation": rec_data,
            "cross_document_consistency": consistency_res,
            "summary_counts": {
                "total": total_count,
                "pass": pass_count,
                "fail": fail_count,
                "review": review_count,
                "insufficient": insufficient_count,
                "not_applicable": na_count
            },
            "requirements": requirement_results
        }
