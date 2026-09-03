from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.core.domain_vocabulary import ComplianceResultStatus

class BaseChecker(ABC):
    """
    Abstract contract for all modular compliance checkers in the Petroleum & Natural Gas domain.
    Exposes a consistent interface:
    verify(requirement, bidder, evidence_context) -> {
        "status": ComplianceResultStatus,
        "confidence": float,
        "evidence": str,
        "reason": str,
        "verification_details": Dict[str, Any]
    }
    """

    @abstractmethod
    def get_checker_name(self) -> str:
        """Returns unique identifier name for the checker."""
        pass

    @abstractmethod
    def verify(
        self,
        requirement: Dict[str, Any],
        bidder: Dict[str, Any],
        evidence_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes domain verification logic.
        Args:
            requirement: Requirement clause dictionary (threshold, category, mandatory, etc.)
            bidder: Bidder entity dictionary (legal_name, pan, gstin, projects, personnel)
            evidence_context: Extracted entities, document chunks, and supporting records
        Returns:
            Structured verification result payload.
        """
        pass
