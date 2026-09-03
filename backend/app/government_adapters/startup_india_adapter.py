from typing import Dict, Any
from app.government_adapters.base_adapter import GovernmentPortalAdapter

class StartupIndiaPortalAdapter(GovernmentPortalAdapter):
    """Mock DPIIT Startup India Adapter."""
    def __init__(self):
        super().__init__(portal_name="STARTUP_INDIA_PORTAL")

    def verify_identity(self, identifier: str, claimed_name: str) -> Dict[str, Any]:
        return self._format_response(
            status="RECOGNIZED",
            is_valid=True,
            data={
                "dpiit_number": identifier or "DIPP12345",
                "entity_name": claimed_name,
                "recognition_date": "2022-03-14",
                "tax_exemption_80iac": True
            },
            message="DPIIT Startup India recognition confirmed"
        )

    def verify_registration(self, identifier: str) -> Dict[str, Any]:
        return self.verify_identity(identifier, "")

    def get_status(self, identifier: str) -> Dict[str, Any]:
        return self.verify_registration(identifier)

    def get_compliance_data(self, identifier: str) -> Dict[str, Any]:
        return self.verify_registration(identifier)


class NSICPortalAdapter(GovernmentPortalAdapter):
    """Mock National Small Industries Corporation (NSIC) Adapter."""
    def __init__(self):
        super().__init__(portal_name="NSIC_PORTAL")

    def verify_identity(self, identifier: str, claimed_name: str) -> Dict[str, Any]:
        return self._format_response(
            status="REGISTERED",
            is_valid=True,
            data={
                "sprs_number": identifier or "NSIC/GP/DEL/2021/0084",
                "valid_upto": "2027-03-31",
                "store_details": "IT Hardware and Networking Systems",
                "monetary_limit_lakhs": 500.0
            },
            message="NSIC Single Point Registration valid"
        )

    def verify_registration(self, identifier: str) -> Dict[str, Any]:
        return self.verify_identity(identifier, "")

    def get_status(self, identifier: str) -> Dict[str, Any]:
        return self.verify_registration(identifier)

    def get_compliance_data(self, identifier: str) -> Dict[str, Any]:
        return self.verify_registration(identifier)
