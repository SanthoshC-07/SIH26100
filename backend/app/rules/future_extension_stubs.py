from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

class BaseComplianceCheckExtension(ABC):
    """
    Abstract base class for all pluggable compliance verification extensions.
    Enables future expansion for statutory, technical, and regulatory portals.
    """
    @abstractmethod
    def get_check_name(self) -> str:
        pass

    @abstractmethod
    def evaluate(self, bidder_data: Dict[str, Any], entities: List[Dict[str, Any]], mandatory: bool = True) -> Dict[str, Any]:
        pass


class UdyamMSMEExtensionStub(BaseComplianceCheckExtension):
    def get_check_name(self) -> str:
        return "UDYAM_MSME"

    def evaluate(self, bidder_data: Dict[str, Any], entities: List[Dict[str, Any]], mandatory: bool = False) -> Dict[str, Any]:
        return {
            "status": "NOT_APPLICABLE",
            "confidence": 1.0,
            "reason": "Extension stub: MSME/Udyam exemption check ready for portal integration.",
            "evidence": "Future check interface enabled.",
            "source": "EXTENSION_STUB",
            "method": "STUB_INTERFACE"
        }


class EPFOExtensionStub(BaseComplianceCheckExtension):
    def get_check_name(self) -> str:
        return "EPFO"

    def evaluate(self, bidder_data: Dict[str, Any], entities: List[Dict[str, Any]], mandatory: bool = False) -> Dict[str, Any]:
        return {
            "status": "NOT_APPLICABLE",
            "confidence": 1.0,
            "reason": "Extension stub: EPFO electronic challan remittance verification ready for portal integration.",
            "evidence": "Future check interface enabled.",
            "source": "EXTENSION_STUB",
            "method": "STUB_INTERFACE"
        }


class ESICExtensionStub(BaseComplianceCheckExtension):
    def get_check_name(self) -> str:
        return "ESIC"

    def evaluate(self, bidder_data: Dict[str, Any], entities: List[Dict[str, Any]], mandatory: bool = False) -> Dict[str, Any]:
        return {
            "status": "NOT_APPLICABLE",
            "confidence": 1.0,
            "reason": "Extension stub: ESIC statutory contribution check ready for portal integration.",
            "evidence": "Future check interface enabled.",
            "source": "EXTENSION_STUB",
            "method": "STUB_INTERFACE"
        }


class StartupIndiaExtensionStub(BaseComplianceCheckExtension):
    def get_check_name(self) -> str:
        return "STARTUP_INDIA"

    def evaluate(self, bidder_data: Dict[str, Any], entities: List[Dict[str, Any]], mandatory: bool = False) -> Dict[str, Any]:
        return {
            "status": "NOT_APPLICABLE",
            "confidence": 1.0,
            "reason": "Extension stub: DPIIT Startup India recognition and prior experience waiver stub.",
            "evidence": "Future check interface enabled.",
            "source": "EXTENSION_STUB",
            "method": "STUB_INTERFACE"
        }


class NSICExtensionStub(BaseComplianceCheckExtension):
    def get_check_name(self) -> str:
        return "NSIC"

    def evaluate(self, bidder_data: Dict[str, Any], entities: List[Dict[str, Any]], mandatory: bool = False) -> Dict[str, Any]:
        return {
            "status": "NOT_APPLICABLE",
            "confidence": 1.0,
            "reason": "Extension stub: NSIC Single Point Registration check ready.",
            "evidence": "Future check interface enabled.",
            "source": "EXTENSION_STUB",
            "method": "STUB_INTERFACE"
        }


class DigiLockerExtensionStub(BaseComplianceCheckExtension):
    def get_check_name(self) -> str:
        return "DIGILOCKER"

    def evaluate(self, bidder_data: Dict[str, Any], entities: List[Dict[str, Any]], mandatory: bool = False) -> Dict[str, Any]:
        return {
            "status": "NOT_APPLICABLE",
            "confidence": 1.0,
            "reason": "Extension stub: DigiLocker document authenticity token verification ready.",
            "evidence": "Future check interface enabled.",
            "source": "EXTENSION_STUB",
            "method": "STUB_INTERFACE"
        }


class EquipmentMachineryExtensionStub(BaseComplianceCheckExtension):
    def get_check_name(self) -> str:
        return "EQUIPMENT_MACHINERY"

    def evaluate(self, bidder_data: Dict[str, Any], entities: List[Dict[str, Any]], mandatory: bool = False) -> Dict[str, Any]:
        return {
            "status": "NOT_APPLICABLE",
            "confidence": 1.0,
            "reason": "Extension stub: Specialized pipeline construction equipment availability check (Sidebooms, HDD rigs, Internal Lineup Clamps, Automatic Welding rigs).",
            "evidence": "Future check interface enabled.",
            "source": "EXTENSION_STUB",
            "method": "STUB_INTERFACE"
        }


class QualityCertificationsExtensionStub(BaseComplianceCheckExtension):
    def get_check_name(self) -> str:
        return "QUALITY_CERTIFICATIONS"

    def evaluate(self, bidder_data: Dict[str, Any], entities: List[Dict[str, Any]], mandatory: bool = False) -> Dict[str, Any]:
        return {
            "status": "NOT_APPLICABLE",
            "confidence": 1.0,
            "reason": "Extension stub: ISO 9001:2015 Quality Management System verification ready.",
            "evidence": "Future check interface enabled.",
            "source": "EXTENSION_STUB",
            "method": "STUB_INTERFACE"
        }
