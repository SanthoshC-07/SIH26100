from typing import Dict, Any
from app.checkers.base_checker import BaseChecker
from app.rules.hse_safety_rule import HSESafetyRuleEngine
from app.rules.oem_rule import OEMRuleEngine
from app.rules.local_content_rule import LocalContentRuleEngine

class TenderSpecificChecker(BaseChecker):
    """
    Check 7: Configurable Petroleum Tender-Specific Check
    Dispatches to:
    - HSE_SAFETY: ISO 45001 / ISO 14001 & Corporate Safety Policy
    - OEM_AUTHORIZATION: Line Pipe / Valve Manufacturer Authorization
    - LOCAL_CONTENT: Make in India (Class-I / Class-II Supplier percentage)
    """
    def get_checker_name(self) -> str:
        return "TenderSpecificChecker"

    def verify(
        self,
        requirement: Dict[str, Any],
        bidder: Dict[str, Any],
        evidence_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        cat = (requirement.get("category") or "HSE_SAFETY").upper()
        bidder_name = bidder.get("legal_name") or bidder.get("bidder_name", "")
        entities = evidence_context.get("entities", [])
        mandatory = requirement.get("mandatory", True)
        tender_number = evidence_context.get("tender_number", "")

        if cat in ["HSE_SAFETY", "HSE", "SAFETY"]:
            res = HSESafetyRuleEngine.evaluate(bidder_name, entities, mandatory)
        elif cat in ["OEM", "OEM_AUTHORIZATION"]:
            res = OEMRuleEngine.evaluate(bidder_name, tender_number, entities, mandatory)
        elif cat in ["LOCAL_CONTENT", "MAKE_IN_INDIA"]:
            threshold = requirement.get("threshold", 50.0)
            res = LocalContentRuleEngine.evaluate(threshold, entities, mandatory)
        else:
            # Default to HSE Safety verification
            res = HSESafetyRuleEngine.evaluate(bidder_name, entities, mandatory)

        return {
            "status": res.get("status", "REVIEW"),
            "confidence": res.get("confidence", 0.95),
            "evidence": res.get("evidence", ""),
            "reason": res.get("reason", ""),
            "document_id": res.get("document_id"),
            "document_name": res.get("document_name"),
            "page_number": res.get("page_number", 1),
            "source": res.get("source", "TENDER_SPECIFIC_RULE_ENGINE"),
            "method": res.get("method", "DOMAIN_RULE_VERIFICATION"),
            "verification_details": res.get("calculation_breakdown", {})
        }
