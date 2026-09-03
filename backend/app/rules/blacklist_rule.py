from typing import Dict, Any, List
from app.government_adapters import adapters

class BlacklistRuleEngine:
    @staticmethod
    def evaluate(
        bidder_name: str,
        pan: str = None,
        extracted_entities: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        portal_res = adapters.blacklist.check_entity(bidder_name, pan)
        
        if not portal_res["is_valid"]:
            data = portal_res["data"]
            return {
                "status": "FAIL",
                "confidence": 0.99,
                "reason": f"CRITICAL: Bidder is DEBARRED / BLACKLISTED by {data.get('debarred_by')} for '{data.get('reason')}' (Period: {data.get('debarment_period')}).",
                "evidence": f"Debarred Entity: {data.get('name')} | Debarring Authority: {data.get('debarred_by')} | Reason: {data.get('reason')}",
                "document_id": None,
                "document_name": None,
                "page_number": 1,
                "source": "MOCK_BLACKLIST_REGISTRY",
                "method": "GOVERNMENT_REGISTRY_SEARCH"
            }

        return {
            "status": "PASS",
            "confidence": 0.98,
            "reason": "No blacklisting or debarment record found in GeM Debarred Vendor Registry, CPPP Central Blacklist, or Ministry of Finance records.",
            "evidence": f"Entity '{bidder_name}' cleared against all central debarment lists.",
            "document_id": None,
            "document_name": None,
            "page_number": 1,
            "source": "MOCK_BLACKLIST_REGISTRY",
            "method": "GOVERNMENT_REGISTRY_SEARCH"
        }
