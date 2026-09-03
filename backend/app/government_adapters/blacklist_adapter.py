import re
from typing import Dict, Any, List
from app.government_adapters.base_adapter import GovernmentPortalAdapter

class BlacklistDebarmentAdapter(GovernmentPortalAdapter):
    """
    Mock Central Debarment / Blacklisting Portal Adapter.
    Integrates GeM debarred vendor registry, CPP portal blacklist, and Ministry exclusion databases.
    """
    
    # Mock registry of debarred/blacklisted entities
    DEBARRED_ENTITIES = [
        {
            "name": "Fraudulent Tech Solutions Ltd",
            "pan": "AABCF9999Z",
            "cin": "U72200DL2018PTC999999",
            "debarred_by": "Ministry of Electronics & Information Technology",
            "reason": "Submission of forged OEM authorization certificate",
            "debarment_period": "2024-01-15 to 2027-01-14",
            "status": "DEBARRED"
        },
        {
            "name": "Corrupt Infratech Pvt Ltd",
            "pan": "AABCC7777K",
            "cin": "U45200MH2017PTC777777",
            "debarred_by": "Department of Expenditure, Ministry of Finance",
            "reason": "Non-performance and breach of integrity pact in tender GeM/2023/B/1102",
            "debarment_period": "2025-06-01 to 2028-05-31",
            "status": "DEBARRED"
        }
    ]

    def __init__(self):
        super().__init__(portal_name="DEBARMENT_REGISTRY")

    def _normalize(self, text: str) -> str:
        if not text:
            return ""
        t = text.lower()
        t = re.sub(r"\b(pvt|private|ltd|limited|llp|inc|corp|co)\b", "", t)
        t = re.sub(r"[^\w\s]", "", t)
        return " ".join(t.split())

    def check_entity(self, company_name: str, pan: str = None) -> Dict[str, Any]:
        norm_name = self._normalize(company_name)
        
        for item in self.DEBARRED_ENTITIES:
            # Check PAN match
            if pan and item.get("pan") == pan.strip().upper():
                return self._format_response(
                    status="FLAGGED",
                    is_valid=False,
                    data=item,
                    message=f"CRITICAL: Entity is DEBARRED by {item['debarred_by']} for '{item['reason']}'"
                )
            # Check normalized name
            item_norm = self._normalize(item["name"])
            if norm_name and (norm_name == item_norm or norm_name in item_norm or item_norm in norm_name):
                return self._format_response(
                    status="FLAGGED",
                    is_valid=False,
                    data=item,
                    message=f"CRITICAL: Entity name matched debarred record by {item['debarred_by']}"
                )
                
        return self._format_response(
            status="CLEAR",
            is_valid=True,
            data={
                "searched_name": company_name,
                "searched_pan": pan,
                "match_found": False,
                "databases_checked": [
                    "GeM Debarred Vendor Registry",
                    "CPPP Central Blacklist",
                    "Ministry of Finance Debarred List under Rule 151 GFR 2017"
                ]
            },
            message="No blacklisting or debarment record found across government registries"
        )

    def verify_identity(self, identifier: str, claimed_name: str) -> Dict[str, Any]:
        return self.check_entity(claimed_name, identifier)

    def verify_registration(self, identifier: str) -> Dict[str, Any]:
        return self.check_entity("", identifier)

    def get_status(self, identifier: str) -> Dict[str, Any]:
        return self.check_entity("", identifier)

    def get_compliance_data(self, identifier: str) -> Dict[str, Any]:
        return self.check_entity("", identifier)
