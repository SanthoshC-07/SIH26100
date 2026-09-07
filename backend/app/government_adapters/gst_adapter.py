import re
from typing import Dict, Any
from app.government_adapters.base_adapter import GovernmentPortalAdapter

class GSTPortalAdapter(GovernmentPortalAdapter):
    """
    Mock GST Portal Adapter.
    Simulates integration with GST System API / GSTIN verification services.
    """
    
    # Mock Database of Registered GSTINs
    MOCK_GST_REGISTRY = {
        "27AABCA1234F1Z5": {
            "legal_name": "Apex Infotech Solutions Private Limited",
            "trade_name": "Apex Infotech Solutions",
            "gstin": "27AABCA1234F1Z5",
            "pan": "AABCA1234F",
            "registration_date": "2018-06-15",
            "status": "ACTIVE",
            "taxpayer_type": "Regular",
            "principal_address": "Plot 42, Hinjewadi Phase 1, Pune, Maharashtra - 411057",
            "return_filing_status": "COMPLIANT",
            "last_return_period": "2026-07",
            "filing_frequency": "Monthly (GSTR-1, GSTR-3B)"
        },
        "07AABCB5678G1Z2": {
            "legal_name": "Bharat Dynamic Tech LLP",
            "trade_name": "Bharat Dynamic Tech",
            "gstin": "07AABCB5678G1Z2",
            "pan": "AABCB5678G",
            "registration_date": "2021-02-10",
            "status": "ACTIVE",
            "taxpayer_type": "Regular",
            "principal_address": "Unit 204, Okhla Industrial Area Phase 3, New Delhi - 110020",
            "return_filing_status": "COMPLIANT",
            "last_return_period": "2026-07",
            "filing_frequency": "Monthly (GSTR-1, GSTR-3B)"
        },
        "33AABCX9999K1Z8": {
            "legal_name": "Vanguard Systems Limited",
            "trade_name": "Vanguard Systems",
            "gstin": "33AABCX9999K1Z8",
            "pan": "AABCX9999K",
            "registration_date": "2015-11-20",
            "status": "ACTIVE",
            "taxpayer_type": "Regular",
            "principal_address": "88 Mount Road, Guindy, Chennai, Tamil Nadu - 600032",
            "return_filing_status": "COMPLIANT",
            "last_return_period": "2026-07",
            "filing_frequency": "Monthly (GSTR-1, GSTR-3B)"
        },
        "29AABCP1234M1Z5": {
            "legal_name": "Praveen B S Engineering Services Private Limited",
            "trade_name": "Praveen Engineering Services",
            "gstin": "29AABCP1234M1Z5",
            "pan": "AABCP1234M",
            "registration_date": "2016-04-10",
            "status": "ACTIVE",
            "taxpayer_type": "Regular",
            "principal_address": "Plot 18, Peenya Industrial Area, Bengaluru, Karnataka - 560058",
            "return_filing_status": "COMPLIANT",
            "last_return_period": "2026-07",
            "filing_frequency": "Monthly (GSTR-1, GSTR-3B)"
        }
    }

    def __init__(self):
        super().__init__(portal_name="GST_PORTAL")

    def validate_gstin_format(self, gstin: str) -> bool:
        """GSTIN format regex: 2 digits (State code), 10 alphanumeric (PAN), 1 digit/letter (Entity number), 'Z', 1 checksum char"""
        if not gstin:
            return False
        pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
        return bool(re.match(pattern, gstin.strip().upper()))

    def verify_identity(self, identifier: str, claimed_name: str) -> Dict[str, Any]:
        cleaned_gstin = identifier.strip().upper() if identifier else ""
        if not self.validate_gstin_format(cleaned_gstin):
            return self._format_response(
                status="INVALID_FORMAT",
                is_valid=False,
                data={"gstin": cleaned_gstin, "error": "Invalid GSTIN format structure"},
                message="GSTIN format failed statutory regex validation"
            )
        
        record = self.MOCK_GST_REGISTRY.get(cleaned_gstin)
        if not record:
            # Dynamically construct synthetic active record for arbitrary test data if not in static dict
            pan = cleaned_gstin[2:12]
            return self._format_response(
                status="ACTIVE",
                is_valid=True,
                data={
                    "gstin": cleaned_gstin,
                    "legal_name": claimed_name,
                    "trade_name": claimed_name,
                    "pan": pan,
                    "registration_date": "2020-01-01",
                    "status": "ACTIVE",
                    "taxpayer_type": "Regular",
                    "return_filing_status": "COMPLIANT",
                    "principal_address": "Registered Commercial Complex, New Delhi - 110001"
                },
                message="GSTIN verified successfully with GST System"
            )
        
        return self._format_response(
            status=record["status"],
            is_valid=(record["status"] == "ACTIVE"),
            data=record,
            message="GSTIN verified successfully with GST System"
        )

    def verify_registration(self, identifier: str) -> Dict[str, Any]:
        return self.verify_identity(identifier, "")

    def get_status(self, identifier: str) -> Dict[str, Any]:
        res = self.verify_registration(identifier)
        return res

    def get_compliance_data(self, identifier: str) -> Dict[str, Any]:
        res = self.verify_registration(identifier)
        if res["is_valid"]:
            res["data"]["filing_compliance"] = "Up to date (No pending GSTR-3B/1 returns)"
        return res
