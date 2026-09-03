from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from app.core.config import settings

class GovernmentPortalAdapter(ABC):
    """
    Standard interface for all Government Portal Integrations.
    In the hackathon MVP, mock services implement this interface and clearly
    return metadata tagging results as DEMO / MOCK GOVERNMENT SOURCE.
    """
    
    def __init__(self, portal_name: str, source_label: Optional[str] = None):
        self.portal_name = portal_name
        self.source_label = source_label or settings.GOVERNMENT_SOURCE_LABEL
        self.is_mock = settings.USE_MOCK_PORTALS
        
    @abstractmethod
    def verify_identity(self, identifier: str, claimed_name: str) -> Dict[str, Any]:
        """Verify if the entity's claimed name matches government registry records."""
        pass

    @abstractmethod
    def verify_registration(self, identifier: str) -> Dict[str, Any]:
        """Verify if the registration identifier is valid and active."""
        pass

    @abstractmethod
    def get_status(self, identifier: str) -> Dict[str, Any]:
        """Fetch current operational status (e.g., ACTIVE, CANCELLED, SUSPENDED)."""
        pass

    @abstractmethod
    def get_compliance_data(self, identifier: str) -> Dict[str, Any]:
        """Fetch detailed compliance data (e.g. return filing status, debarment list)."""
        pass
        
    def _format_response(
        self,
        status: str,
        is_valid: bool,
        data: Dict[str, Any],
        message: str = "Verification successful"
    ) -> Dict[str, Any]:
        return {
            "portal": self.portal_name,
            "source_type": self.source_label,
            "status": status,
            "is_valid": is_valid,
            "message": message,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "adapter_version": "1.0-mock" if self.is_mock else "1.0-live"
        }
