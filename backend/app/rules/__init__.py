from app.rules.gst_rule import GSTRuleEngine
from app.rules.pan_rule import PANRuleEngine, UdyamRuleEngine
from app.rules.turnover_rule import TurnoverRuleEngine
from app.rules.oil_gas_experience_rule import OilGasExperienceRuleEngine
from app.rules.similar_pipeline_rule import SimilarPipelineRuleEngine
from app.rules.technical_manpower_rule import TechnicalManpowerRuleEngine
from app.rules.local_content_rule import LocalContentRuleEngine
from app.rules.oem_rule import OEMRuleEngine
from app.rules.hse_safety_rule import HSESafetyRuleEngine
from app.rules.blacklist_rule import BlacklistRuleEngine
from app.rules.cross_document_rule import CrossDocumentConsistencyEngine
from app.rules.future_extension_stubs import (
    BaseComplianceCheckExtension,
    UdyamMSMEExtensionStub,
    EPFOExtensionStub,
    ESICExtensionStub,
    StartupIndiaExtensionStub,
    NSICExtensionStub,
    DigiLockerExtensionStub,
    EquipmentMachineryExtensionStub,
    QualityCertificationsExtensionStub
)

__all__ = [
    # 7 Core Compliance Checks
    "GSTRuleEngine",                   # Check 1: GST
    "PANRuleEngine",                   # Check 2: PAN
    "TurnoverRuleEngine",              # Check 3: Turnover
    "OilGasExperienceRuleEngine",      # Check 4: Oil & Gas Experience
    "SimilarPipelineRuleEngine",       # Check 5: Similar Pipeline Experience
    "TechnicalManpowerRuleEngine",     # Check 6: Technical Manpower
    "LocalContentRuleEngine",          # Check 7 (Option A: Make in India)
    "OEMRuleEngine",                   # Check 7 (Option B: OEM Authorization)
    "HSESafetyRuleEngine",             # Check 7 (Option C: HSE/Safety Compliance)
    
    # Supporting & Identity Consistency Engines
    "CrossDocumentConsistencyEngine",
    "BlacklistRuleEngine",
    "UdyamRuleEngine",
    
    # Pluggable Architecture Extension Stubs
    "BaseComplianceCheckExtension",
    "UdyamMSMEExtensionStub",
    "EPFOExtensionStub",
    "ESICExtensionStub",
    "StartupIndiaExtensionStub",
    "NSICExtensionStub",
    "DigiLockerExtensionStub",
    "EquipmentMachineryExtensionStub",
    "QualityCertificationsExtensionStub"
]
