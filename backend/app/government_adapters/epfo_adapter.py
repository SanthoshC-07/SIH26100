from typing import Dict, Any
from app.government_adapters.base_adapter import GovernmentPortalAdapter

class EPFOPortalAdapter(GovernmentPortalAdapter):
    """
    Mock EPFO (Employees' Provident Fund Organisation) Portal Adapter.
    """
    def __init__(self):
        super().__init__(portal_name="EPFO_PORTAL")

    def verify_identity(self, identifier: str, claimed_name: str) -> Dict[str, Any]:
        cleaned = identifier.strip() if identifier else ""
        return self._format_response(
            status="ACTIVE",
            is_valid=bool(cleaned),
            data={
                "establishment_code": cleaned or "MH/BAN/0045921/000",
                "establishment_name": claimed_name or "Apex Infotech Solutions Private Limited",
                "coverage_status": "COVERED_ACTIVE",
                "last_ecr_month": "2026-07",
                "wage_month_remittance_status": "PAID"
            },
            message="EPFO establishment compliance verified"
        )

    def verify_registration(self, identifier: str) -> Dict[str, Any]:
        return self.verify_identity(identifier, "")

    def get_status(self, identifier: str) -> Dict[str, Any]:
        return self.verify_registration(identifier)

    def get_compliance_data(self, identifier: str) -> Dict[str, Any]:
        res = self.verify_registration(identifier)
        return res


class ESICPortalAdapter(GovernmentPortalAdapter):
    """
    Mock ESIC (Employees' State Insurance Corporation) Portal Adapter.
    """
    def __init__(self):
        super().__init__(portal_name="ESIC_PORTAL")

    def verify_identity(self, identifier: str, claimed_name: str) -> Dict[str, Any]:
        cleaned = identifier.strip() if identifier else ""
        return self._format_response(
            status="ACTIVE",
            is_valid=bool(cleaned),
            data={
                "employer_code": cleaned or "31000543210000999",
                "employer_name": claimed_name or "Apex Infotech Solutions Private Limited",
                "status": "COMPLIANT",
                "last_contribution_period": "2026-07",
                "default_flag": False
            },
            message="ESIC employer registration and monthly contribution verified"
        )

    def verify_registration(self, identifier: str) -> Dict[str, Any]:
        return self.verify_identity(identifier, "")

    def get_status(self, identifier: str) -> Dict[str, Any]:
        return self.verify_registration(identifier)

    def get_compliance_data(self, identifier: str) -> Dict[str, Any]:
        return self.verify_registration(identifier)
