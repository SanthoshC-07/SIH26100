import re
from typing import Dict, Any
from app.government_adapters.base_adapter import GovernmentPortalAdapter

class UdyamPortalAdapter(GovernmentPortalAdapter):
    """
    Mock Udyam / MSME Portal Adapter.
    Simulates integration with Ministry of MSME Udyam Registration Portal.
    """
    
    MOCK_UDYAM_REGISTRY = {
        "UDYAM-MH-01-0012345": {
            "udyam_number": "UDYAM-MH-01-0012345",
            "enterprise_name": "Apex Infotech Solutions Private Limited",
            "enterprise_type": "MEDIUM", # MICRO, SMALL, MEDIUM
            "major_activity": "Services",
            "nic_codes": ["6201 - Computer programming activities", "6202 - Information technology consultancy"],
            "registration_date": "2020-08-12",
            "dic_name": "Pune",
            "status": "VERIFIED_ACTIVE"
        },
        "UDYAM-DL-02-0054321": {
            "udyam_number": "UDYAM-DL-02-0054321",
            "enterprise_name": "Bharat Dynamic Tech LLP",
            "enterprise_type": "SMALL",
            "major_activity": "Manufacturing & Services",
            "nic_codes": ["2620 - Manufacture of computers and peripheral equipment"],
            "registration_date": "2021-05-18",
            "dic_name": "South Delhi",
            "status": "VERIFIED_ACTIVE"
        },
        "UDYAM-TN-03-0099887": {
            "udyam_number": "UDYAM-TN-03-0099887",
            "enterprise_name": "Vanguard Systems Limited",
            "enterprise_type": "MEDIUM",
            "major_activity": "Services",
            "nic_codes": ["6209 - Other information technology activities"],
            "registration_date": "2020-10-05",
            "dic_name": "Chennai",
            "status": "VERIFIED_ACTIVE"
        }
    }

    def __init__(self):
        super().__init__(portal_name="UDYAM_PORTAL")

    def validate_udyam_format(self, udyam: str) -> bool:
        """Format: UDYAM-XX-00-0000000 (State-2letters, Zone-2digits, Seq-7digits)"""
        if not udyam:
            return False
        pattern = r"^UDYAM-[A-Z]{2}-[0-9]{2}-[0-9]{7}$"
        return bool(re.match(pattern, udyam.strip().upper()))

    def verify_identity(self, identifier: str, claimed_name: str) -> Dict[str, Any]:
        cleaned = identifier.strip().upper() if identifier else ""
        if not self.validate_udyam_format(cleaned):
            return self._format_response(
                status="INVALID_FORMAT",
                is_valid=False,
                data={"udyam_number": cleaned, "error": "Invalid Udyam registration number structure"},
                message="Udyam registration number does not adhere to official pattern (UDYAM-ST-00-0000000)"
            )
        
        record = self.MOCK_UDYAM_REGISTRY.get(cleaned)
        if not record:
            return self._format_response(
                status="ACTIVE",
                is_valid=True,
                data={
                    "udyam_number": cleaned,
                    "enterprise_name": claimed_name,
                    "enterprise_type": "SMALL",
                    "status": "VERIFIED_ACTIVE",
                    "registration_date": "2021-01-01"
                },
                message="Udyam registration verified with Ministry of MSME"
            )

        return self._format_response(
            status=record["status"],
            is_valid=(record["status"] == "VERIFIED_ACTIVE"),
            data=record,
            message="Udyam registration verified with Ministry of MSME"
        )

    def verify_registration(self, identifier: str) -> Dict[str, Any]:
        return self.verify_identity(identifier, "")

    def get_status(self, identifier: str) -> Dict[str, Any]:
        return self.verify_registration(identifier)

    def get_compliance_data(self, identifier: str) -> Dict[str, Any]:
        res = self.verify_registration(identifier)
        if res["is_valid"]:
            res["data"]["msme_benefits_eligible"] = True
            res["data"]["purchase_preference"] = "Eligible under Public Procurement Policy for MSEs Order 2012"
        return res
