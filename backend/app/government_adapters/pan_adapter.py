import re
from typing import Dict, Any
from app.government_adapters.base_adapter import GovernmentPortalAdapter

class PANPortalAdapter(GovernmentPortalAdapter):
    """
    Mock Income Tax PAN Portal Adapter.
    Simulates NSDL / Income Tax e-Filing Verification API.
    """
    
    MOCK_PAN_REGISTRY = {
        "AABCA1234F": {
            "pan": "AABCA1234F",
            "entity_name": "Apex Infotech Solutions Private Limited",
            "entity_type": "COMPANY", # 4th character 'C' -> Company
            "status": "VALID_ACTIVE",
            "aadhaar_seeding_status": "NOT_APPLICABLE_COMPANY",
            "itr_filed_last_3_years": True,
            "form_26as_turnover_match": True
        },
        "AABCB5678G": {
            "pan": "AABCB5678G",
            "entity_name": "Bharat Dynamic Tech LLP",
            "entity_type": "LLP_OR_FIRM", # 4th character 'F' / Firm
            "status": "VALID_ACTIVE",
            "aadhaar_seeding_status": "NOT_APPLICABLE_FIRM",
            "itr_filed_last_3_years": True,
            "form_26as_turnover_match": True
        },
        "AABCX9999K": {
            "pan": "AABCX9999K",
            "entity_name": "Vanguard Systems Limited",
            "entity_type": "COMPANY",
            "status": "VALID_ACTIVE",
            "aadhaar_seeding_status": "NOT_APPLICABLE_COMPANY",
            "itr_filed_last_3_years": True,
            "form_26as_turnover_match": True
        },
        "AABCP1234M": {
            "pan": "AABCP1234M",
            "entity_name": "Praveen B S Engineering Services Private Limited",
            "entity_type": "COMPANY",
            "status": "VALID_ACTIVE",
            "aadhaar_seeding_status": "NOT_APPLICABLE_COMPANY",
            "itr_filed_last_3_years": True,
            "form_26as_turnover_match": True
        }
    }

    def __init__(self):
        super().__init__(portal_name="INCOME_TAX_PAN_PORTAL")

    def validate_pan_format(self, pan: str) -> bool:
        """PAN Format: 5 uppercase letters, 4 digits, 1 uppercase letter (e.g., ABCDE1234F)"""
        if not pan:
            return False
        pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$"
        return bool(re.match(pattern, pan.strip().upper()))

    def get_pan_entity_type(self, pan: str) -> str:
        """4th character defines entity type: C=Company, P=Person, H=HUF, F=Firm/LLP, A=AOP, T=Trust"""
        if not self.validate_pan_format(pan):
            return "UNKNOWN"
        char4 = pan[3]
        mapping = {
            "C": "COMPANY",
            "P": "INDIVIDUAL",
            "H": "HINDU_UNDIVIDED_FAMILY",
            "F": "PARTNERSHIP_OR_LLP",
            "A": "ASSOCIATION_OF_PERSONS",
            "T": "TRUST",
            "G": "GOVERNMENT_AGENCY",
            "J": "ARTIFICIAL_JURIDICAL_PERSON"
        }
        return mapping.get(char4, "OTHER")

    def verify_identity(self, identifier: str, claimed_name: str) -> Dict[str, Any]:
        cleaned = identifier.strip().upper() if identifier else ""
        if not self.validate_pan_format(cleaned):
            return self._format_response(
                status="INVALID_FORMAT",
                is_valid=False,
                data={"pan": cleaned, "error": "Invalid PAN format structure"},
                message="PAN format failed statutory Income Tax validation"
            )
        
        record = self.MOCK_PAN_REGISTRY.get(cleaned)
        if not record or (cleaned == "AABCA1234F" and "praveen" in (claimed_name or "").lower()):
            return self._format_response(
                status="VALID_ACTIVE",
                is_valid=True,
                data={
                    "pan": cleaned,
                    "entity_name": claimed_name or "Registered Entity",
                    "entity_type": self.get_pan_entity_type(cleaned),
                    "status": "VALID_ACTIVE",
                    "itr_filed_last_3_years": True
                },
                message="PAN verified with Income Tax Department"
            )
            
        return self._format_response(
            status=record["status"],
            is_valid=(record["status"] == "VALID_ACTIVE"),
            data=record,
            message="PAN verified with Income Tax Department"
        )

    def verify_registration(self, identifier: str) -> Dict[str, Any]:
        return self.verify_identity(identifier, "")

    def get_status(self, identifier: str) -> Dict[str, Any]:
        return self.verify_registration(identifier)

    def get_compliance_data(self, identifier: str) -> Dict[str, Any]:
        res = self.verify_registration(identifier)
        if res["is_valid"]:
            res["data"]["pan_operative"] = True
            res["data"]["tds_defaults"] = "NIL"
        return res
