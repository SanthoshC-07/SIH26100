from typing import Dict, Any
from app.checkers.base_checker import BaseChecker
from app.rules.pan_rule import PANRuleEngine

class PANChecker(BaseChecker):
    """
    Check 2: PAN & Legal Entity Identity Consistency
    """
    def get_checker_name(self) -> str:
        return "PANChecker"

    def verify(
        self,
        requirement: Dict[str, Any],
        bidder: Dict[str, Any],
        evidence_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        bidder_name = bidder.get("legal_name") or bidder.get("bidder_name", "")
        pan = bidder.get("pan", "")
        entities = evidence_context.get("entities", [])
        mandatory = requirement.get("mandatory", True)

        res = PANRuleEngine.evaluate(bidder_name, pan, entities, mandatory)
        return {
            "status": res.get("status", "REVIEW"),
            "confidence": res.get("confidence", 0.95),
            "evidence": res.get("evidence", ""),
            "reason": res.get("reason", ""),
            "document_id": res.get("document_id"),
            "document_name": res.get("document_name"),
            "page_number": res.get("page_number", 1),
            "source": res.get("source", "MOCK_INCOME_TAX_PORTAL"),
            "method": res.get("method", "RULE_AND_PORTAL"),
            "verification_details": res.get("calculation_breakdown", {})
        }
