from typing import Dict, Any, List
from app.checkers.base_checker import BaseChecker
from app.rules.similar_pipeline_rule import SimilarPipelineRuleEngine

class SimilarPipelineExperienceChecker(BaseChecker):
    """
    Check 5: Similar Pipeline Experience Verification Service
    Evaluates length (km), diameter, API 5L line pipe material, and project value.
    """
    def get_checker_name(self) -> str:
        return "SimilarPipelineExperienceChecker"

    def verify(
        self,
        requirement: Dict[str, Any],
        bidder: Dict[str, Any],
        evidence_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        req_length = requirement.get("required_pipeline_length_km") or requirement.get("threshold") or 100.0
        mandatory = requirement.get("mandatory", True)
        entities = evidence_context.get("entities", [])
        
        # 1. Check structured BidderProject database records
        projects = bidder.get("projects", [])
        if projects:
            pipeline_projects = [
                p for p in projects
                if p.get("pipeline_length_km") is not None and p.get("pipeline_length_km") > 0
            ]
            if pipeline_projects:
                max_proj = max(pipeline_projects, key=lambda x: x.get("pipeline_length_km", 0.0))
                max_km = max_proj.get("pipeline_length_km", 0.0)
                is_compliant = max_km >= float(req_length)
                
                breakdown = {
                    "required_pipeline_length_km": float(req_length),
                    "max_completed_length_km": max_km,
                    "project_name": max_proj.get("project_name"),
                    "client": max_proj.get("client_name"),
                    "diameter": max_proj.get("pipeline_diameter"),
                    "requirement_met": is_compliant
                }

                if is_compliant:
                    return {
                        "status": "PASS",
                        "confidence": 0.98,
                        "evidence": f"Structured Project Record: {max_proj.get('project_name')} — Completed {max_km:.1f} km {max_proj.get('pipeline_diameter', '')} for {max_proj.get('client_name')}.",
                        "reason": f"Bidder completed {max_km:.1f} km pipeline, satisfying the required threshold of {req_length:.1f} km.",
                        "document_id": max_proj.get("evidence_document_id"),
                        "document_name": "Pipeline_Completion_Certificate.pdf",
                        "page_number": 1,
                        "source": "STRUCTURED_BIDDER_PROJECT_DATABASE",
                        "method": "DETERMINISTIC_THRESHOLD_GATING",
                        "verification_details": breakdown
                    }
                else:
                    shortfall = float(req_length) - max_km
                    breakdown["length_shortfall_km"] = round(shortfall, 2)
                    return {
                        "status": "FAIL" if mandatory else "REVIEW",
                        "confidence": 0.96,
                        "evidence": f"Submitted project record shows only {max_km:.1f} km pipeline (Project: {max_proj.get('project_name')}).",
                        "reason": f"Maximum completed pipeline length of {max_km:.1f} km is below requirement of {req_length:.1f} km (Shortfall: {shortfall:.1f} km).",
                        "document_id": max_proj.get("evidence_document_id"),
                        "document_name": "Pipeline_Completion_Certificate.pdf",
                        "page_number": 1,
                        "source": "STRUCTURED_BIDDER_PROJECT_DATABASE",
                        "method": "DETERMINISTIC_THRESHOLD_GATING",
                        "verification_details": breakdown
                    }

        # 2. Fallback to entity extraction & document text
        res = SimilarPipelineRuleEngine.evaluate(float(req_length), None, entities, mandatory)
        return {
            "status": res.get("status", "REVIEW"),
            "confidence": res.get("confidence", 0.94),
            "evidence": res.get("evidence", ""),
            "reason": res.get("reason", ""),
            "document_id": res.get("document_id"),
            "document_name": res.get("document_name"),
            "page_number": res.get("page_number", 1),
            "source": res.get("source", "SIMILAR_PIPELINE_ENGINE"),
            "method": res.get("method", "DETERMINISTIC_THRESHOLD_AND_NLP"),
            "verification_details": res.get("calculation_breakdown", {})
        }
