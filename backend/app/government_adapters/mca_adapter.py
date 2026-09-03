import re
from typing import Dict, Any
from app.government_adapters.base_adapter import GovernmentPortalAdapter

class MCAPortalAdapter(GovernmentPortalAdapter):
    """
    Mock Ministry of Corporate Affairs (MCA21) Portal Adapter.
    Validates CIN (Corporate Identification Number) and Company Master Data.
    """
    
    def __init__(self):
        super().__init__(portal_name="MCA21_PORTAL")

    def validate_cin_format(self, cin: str) -> bool:
        """CIN Format: 21 chars: [L/U][5 digits][2 state letters][4 year digits][3 entity chars][6 digits]"""
        if not cin:
            return False
        pattern = r"^[LU][0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6}$"
        return bool(re.match(pattern, cin.strip().upper()))

    def verify_identity(self, identifier: str, claimed_name: str) -> Dict[str, Any]:
        cleaned = identifier.strip().upper() if identifier else ""
        if cleaned and not self.validate_cin_format(cleaned):
            return self._format_response(
                status="INVALID_FORMAT",
                is_valid=False,
                data={"cin": cleaned, "error": "Invalid CIN structure"},
                message="CIN failed MCA21 format validation"
            )
            
        return self._format_response(
            status="ACTIVE",
            is_valid=True,
            data={
                "cin": cleaned or "U72200MH2018PTC309871",
                "company_name": claimed_name or "Apex Infotech Solutions Private Limited",
                "company_status": "ACTIVE",
                "company_category": "Company limited by Shares",
                "class_of_company": "Private",
                "authorized_capital_inr": 50000000.0,
                "paid_up_capital_inr": 25000000.0,
                "date_of_incorporation": "2018-04-12"
            },
            message="Company master data verified with MCA21"
        )

    def verify_registration(self, identifier: str) -> Dict[str, Any]:
        return self.verify_identity(identifier, "")

    def get_status(self, identifier: str) -> Dict[str, Any]:
        return self.verify_identity(identifier, "")

    def get_compliance_data(self, identifier: str) -> Dict[str, Any]:
        return self.verify_identity(identifier, "")
