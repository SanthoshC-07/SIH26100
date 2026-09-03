from enum import Enum
from typing import List, Dict, Set

# =====================================================================
# MINISTRY OF PETROLEUM & NATURAL GAS (MoPNG) - DOMAIN VOCABULARY
# =====================================================================

class SectorType(str, Enum):
    OIL_AND_GAS = "OIL_AND_GAS"
    PETROLEUM = "PETROLEUM"
    NATURAL_GAS = "NATURAL_GAS"
    REFINERY = "REFINERY"
    PETROCHEMICAL = "PETROCHEMICAL"
    GAS_TRANSMISSION = "GAS_TRANSMISSION"
    CITY_GAS_DISTRIBUTION = "CITY_GAS_DISTRIBUTION"

class TenderType(str, Enum):
    PIPELINE_PROCUREMENT = "PIPELINE_PROCUREMENT"
    PIPELINE_EPC = "PIPELINE_EPC"
    PIPELINE_LAYING = "PIPELINE_LAYING"
    PIPELINE_CONSTRUCTION = "PIPELINE_CONSTRUCTION"
    PIPELINE_REHABILITATION = "PIPELINE_REHABILITATION"
    PIPELINE_MAINTENANCE = "PIPELINE_MAINTENANCE"
    EQUIPMENT_PROCUREMENT = "EQUIPMENT_PROCUREMENT"

class ProjectType(str, Enum):
    PIPELINE_CONSTRUCTION = "PIPELINE_CONSTRUCTION"
    PIPELINE_LAYING = "PIPELINE_LAYING"
    PIPELINE_EPC = "PIPELINE_EPC"
    PIPELINE_REHABILITATION = "PIPELINE_REHABILITATION"
    PIPELINE_MAINTENANCE = "PIPELINE_MAINTENANCE"
    HDD_RIVER_CROSSING = "HDD_RIVER_CROSSING"
    COMPRESSOR_STATION_EPC = "COMPRESSOR_STATION_EPC"
    SV_STATION_INSTALLATION = "SV_STATION_INSTALLATION"

class PipelineType(str, Enum):
    NATURAL_GAS = "NATURAL_GAS"
    CRUDE_OIL = "CRUDE_OIL"
    PRODUCT_PIPELINE = "PRODUCT_PIPELINE"
    CROSS_COUNTRY_PIPELINE = "CROSS_COUNTRY_PIPELINE"
    TRANSMISSION_PIPELINE = "TRANSMISSION_PIPELINE"
    OFFSHORE_FEEDER = "OFFSHORE_FEEDER"
    CGD_STEEL_NETWORK = "CGD_STEEL_NETWORK"
    OTHER = "OTHER"

class BidderRole(str, Enum):
    EPC_CONTRACTOR = "EPC_CONTRACTOR"
    MAIN_CONTRACTOR = "MAIN_CONTRACTOR"
    SUBCONTRACTOR = "SUBCONTRACTOR"
    JV_PARTNER = "JV_PARTNER"
    DESIGN_CONTRACTOR = "DESIGN_CONTRACTOR"
    CONSTRUCTION_CONTRACTOR = "CONSTRUCTION_CONTRACTOR"

class ScopeOfWork(str, Enum):
    PIPELINE_LAYING = "PIPELINE_LAYING"
    PIPELINE_CONSTRUCTION = "PIPELINE_CONSTRUCTION"
    HYDROTESTING = "HYDROTESTING"
    HDD = "HDD"
    CROSSING_WORK = "CROSSING_WORK"
    WELDING = "WELDING"
    COMMISSIONING = "COMMISSIONING"
    ENGINEERING = "ENGINEERING"
    PROCUREMENT = "PROCUREMENT"
    EPC = "EPC"
    CATHODIC_PROTECTION = "CATHODIC_PROTECTION"
    SCADA_TELEMETRY = "SCADA_TELEMETRY"

class DocumentType(str, Enum):
    # Tender Documents
    TENDER_DOCUMENT = "TENDER_DOCUMENT"
    ELIGIBILITY_CRITERIA = "ELIGIBILITY_CRITERIA"
    TECHNICAL_SPECIFICATION = "TECHNICAL_SPECIFICATION"
    BOQ = "BOQ"
    SCOPE_OF_WORK = "SCOPE_OF_WORK"
    # Bidder Documents
    GST_CERTIFICATE = "GST_CERTIFICATE"
    PAN_DOCUMENT = "PAN_DOCUMENT"
    FINANCIAL_STATEMENT = "FINANCIAL_STATEMENT"
    CA_CERTIFICATE = "CA_CERTIFICATE"
    EXPERIENCE_CERTIFICATE = "EXPERIENCE_CERTIFICATE"
    WORK_ORDER = "WORK_ORDER"
    COMPLETION_CERTIFICATE = "COMPLETION_CERTIFICATE"
    PIPELINE_PROJECT_DOCUMENT = "PIPELINE_PROJECT_DOCUMENT"
    PERSONNEL_CV = "PERSONNEL_CV"
    TECHNICAL_DOCUMENT = "TECHNICAL_DOCUMENT"
    OEM_AUTHORIZATION = "OEM_AUTHORIZATION"
    HSE_DOCUMENT = "HSE_DOCUMENT"
    LOCAL_CONTENT_DECLARATION = "LOCAL_CONTENT_DECLARATION"
    OTHER = "OTHER"

class ExtractionMethod(str, Enum):
    PDF_TEXT = "PDF_TEXT"
    TESSERACT_OCR = "TESSERACT_OCR"
    MANUAL_REVIEW = "MANUAL_REVIEW"

class ComplianceResultStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    REVIEW = "REVIEW"
    INSUFFICIENT = "INSUFFICIENT"
    NOT_APPLICABLE = "NOT_APPLICABLE"

# Centralized Petroleum & Pipeline Domain Keywords Dictionary
PETROLEUM_DOMAIN_DICTIONARY: Dict[str, List[str]] = {
    "SECTORS": [
        "Oil & Gas", "Natural Gas", "Crude Oil", "Petroleum Products", "Refinery",
        "Petrochemical", "Gas Transmission", "Oil Transmission", "Hydrocarbon",
        "City Gas Distribution", "LNG Terminal", "LPG Bottling"
    ],
    "PIPELINE_TERMS": [
        "Pipeline", "Cross-country Pipeline", "Transmission Pipeline", "Gas Pipeline",
        "Crude Pipeline", "Product Pipeline", "Spur Line", "Feeder Line", "Steel Pipeline",
        "API 5L", "Grade X70", "Grade X65", "Grade X80", "Carbon Steel", "ERW", "LSAW", "HSAW"
    ],
    "ENGINEERING_OPERATIONS": [
        "EPC", "Pipeline Laying", "Pipeline Construction", "Hydrotesting", "HDD",
        "Horizontal Directional Drilling", "Crossing Work", "Welding", "Commissioning",
        "Pre-commissioning", "Right of Way", "ROW Clearance", "Trenching", "Lowering",
        "Backfilling", "Cathodic Protection", "SCADA", "Pressure Testing", "Pigging",
        "Sectionalizing Valve", "SV Station", "Intermediate Pigging Station", "IP Station"
    ],
    "COMPLIANCE_AREAS": [
        "GST", "PAN", "Turnover", "Oil & Gas Experience", "Similar Pipeline Experience",
        "Technical Manpower", "HSE", "Health Safety Environment", "ISO 45001", "ISO 14001",
        "OEM Authorization", "Make in India", "Local Content", "Class-I Local Supplier"
    ],
    "QUALIFICATIONS": [
        "B.Tech Mechanical", "B.E. Mechanical", "Pipeline Engineer", "Welding Inspector",
        "NDT Level II", "NDT Level III", "Safety Officer", "QA/QC Inspector", "Corrosion Engineer"
    ]
}

def is_petroleum_relevant(text: str) -> bool:
    """Checks if a given string contains relevant petroleum/pipeline domain concepts."""
    lower_text = text.lower()
    for category, terms in PETROLEUM_DOMAIN_DICTIONARY.items():
        if any(term.lower() in lower_text for term in terms):
            return True
    return False
