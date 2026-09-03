from typing import Dict, Any
from app.checkers.base_checker import BaseChecker
from app.rules.turnover_rule import TurnoverRuleEngine

class TurnoverChecker(BaseChecker):
    """
    Check 3: Financial Turnover Deterministic Arithmetic
    """
    def get_checker_name(self) -> str:
        return "TurnoverChecker"

    def verify(
        self,
        requirement: Dict[str, Any],
        bidder: Dict[str, Any],
        evidence_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        threshold = requirement.get("threshold", 100000000.0)
        entities = evidence_context.get("entities", [])
        mandatory = requirement.get("mandatory", True)

        res = TurnoverRuleEngine.evaluate(threshold, entities, mandatory)
        return {
            "status": res.get("status", "REVIEW"),
            "confidence": res.get("confidence", 0.98),
            "evidence": res.get("evidence", ""),
            "reason": res.get("reason", ""),
            "document_id": res.get("document_id"),
            "document_name": res.get("document_name"),
            "page_number": res.get("page_number", 1),
            "source": res.get("source", "RULE_ENGINE"),
            "method": res.get("method", "DETERMINISTIC_PYTHON_ARITHMETIC"),
            "verification_details": res.get("calculation_breakdown", {})
        }
