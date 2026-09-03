from typing import Dict, Any
from app.checkers.base_checker import BaseChecker
from app.rules.gst_rule import GSTRuleEngine

class GSTChecker(BaseChecker):
    """
    Check 1: GST Statutory Registration & Active Status
    """
    def get_checker_name(self) -> str:
        return "GSTChecker"

    def verify(
        self,
        requirement: Dict[str, Any],
        bidder: Dict[str, Any],
        evidence_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        bidder_name = bidder.get("legal_name") or bidder.get("bidder_name", "")
        gstin = bidder.get("gstin", "")
        entities = evidence_context.get("entities", [])
        mandatory = requirement.get("mandatory", True)

        res = GSTRuleEngine.evaluate(bidder_name, gstin, entities, mandatory)
        return {
            "status": res.get("status", "REVIEW"),
            "confidence": res.get("confidence", 0.95),
            "evidence": res.get("evidence", ""),
            "reason": res.get("reason", ""),
            "document_id": res.get("document_id"),
            "document_name": res.get("document_name"),
            "page_number": res.get("page_number", 1),
            "source": res.get("source", "MOCK_GST_PORTAL"),
            "method": res.get("method", "RULE_AND_PORTAL"),
            "verification_details": res.get("calculation_breakdown", {})
        }
