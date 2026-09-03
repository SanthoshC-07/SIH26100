from typing import Dict, Any, List
from app.checkers.base_checker import BaseChecker
from app.rules.oil_gas_experience_rule import OilGasExperienceRuleEngine
from app.core.domain_vocabulary import is_petroleum_relevant

class OilGasExperienceChecker(BaseChecker):
    """
    Check 4: Oil & Gas / Hydrocarbon Sector Experience
    Evaluates both structured BidderProject database records and extracted document evidence.
    """
    def get_checker_name(self) -> str:
        return "OilGasExperienceChecker"

    def verify(
        self,
        requirement: Dict[str, Any],
        bidder: Dict[str, Any],
        evidence_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        bidder_name = bidder.get("legal_name") or bidder.get("bidder_name", "")
        entities = evidence_context.get("entities", [])
        doc_chunks = evidence_context.get("doc_chunks", [])
        mandatory = requirement.get("mandatory", True)
        
        # Check structured BidderProject entities
        projects = bidder.get("projects", [])
        qualifying_db_projects = [
            p for p in projects
            if p.get("sector", "").upper() in ["OIL_AND_GAS", "PETROLEUM", "REFINERY", "NATURAL_GAS"]
            or is_petroleum_relevant(p.get("project_name", "") + " " + p.get("scope_of_work", ""))
        ]

        if qualifying_db_projects:
            best_p = qualifying_db_projects[0]
            return {
                "status": "PASS",
                "confidence": 0.98,
                "evidence": f"Structured Project Record: {best_p.get('project_name')} (Client: {best_p.get('client_name')}, Value: INR {best_p.get('project_value', 0)/1e7:.2f} Cr, Scope: {best_p.get('scope_of_work')})",
                "reason": f"Bidder demonstrates verified execution across {len(qualifying_db_projects)} petroleum/gas project record(s) in database.",
                "document_id": best_p.get("evidence_document_id"),
                "document_name": "Project_Completion_Certificate.pdf",
                "page_number": 1,
                "source": "STRUCTURED_BIDDER_PROJECT_DATABASE",
                "method": "DOMAIN_TAXONOMY_MATCH",
                "verification_details": {
                    "total_qualifying_projects": len(qualifying_db_projects),
                    "project_names": [p.get("project_name") for p in qualifying_db_projects]
                }
            }

        # Fallback to Rule Engine & Semantic analysis on extracted text
        res = OilGasExperienceRuleEngine.evaluate(bidder_name, entities, mandatory, doc_chunks)
        return {
            "status": res.get("status", "REVIEW"),
            "confidence": res.get("confidence", 0.90),
            "evidence": res.get("evidence", ""),
            "reason": res.get("reason", ""),
            "document_id": res.get("document_id"),
            "document_name": res.get("document_name"),
            "page_number": res.get("page_number", 1),
            "source": res.get("source", "SEMANTIC_EXPERIENCE_MATCHER"),
            "method": res.get("method", "NLP_DOMAIN_CLASSIFICATION"),
            "verification_details": res.get("calculation_breakdown", {})
        }
