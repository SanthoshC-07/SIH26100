from app.checkers.base_checker import BaseChecker
from app.checkers.gst_checker import GSTChecker
from app.checkers.pan_checker import PANChecker
from app.checkers.turnover_checker import TurnoverChecker
from app.checkers.oil_gas_experience_checker import OilGasExperienceChecker
from app.checkers.similar_pipeline_checker import SimilarPipelineExperienceChecker
from app.checkers.technical_manpower_checker import TechnicalManpowerChecker
from app.checkers.tender_specific_checker import TenderSpecificChecker

CHECKER_REGISTRY = {
    "GST": GSTChecker(),
    "PAN": PANChecker(),
    "TURNOVER": TurnoverChecker(),
    "OIL_GAS_EXPERIENCE": OilGasExperienceChecker(),
    "SIMILAR_PIPELINE_EXPERIENCE": SimilarPipelineExperienceChecker(),
    "TECHNICAL_MANPOWER": TechnicalManpowerChecker(),
    "HSE_SAFETY": TenderSpecificChecker(),
    "OEM_AUTHORIZATION": TenderSpecificChecker(),
    "OEM": TenderSpecificChecker(),
    "LOCAL_CONTENT": TenderSpecificChecker()
}

def get_checker_for_category(category: str) -> BaseChecker:
    cat = (category or "").upper()
    if cat in CHECKER_REGISTRY:
        return CHECKER_REGISTRY[cat]
    if "PIPELINE" in cat:
        return CHECKER_REGISTRY["SIMILAR_PIPELINE_EXPERIENCE"]
    if "OIL" in cat or "GAS" in cat or "EXPERIENCE" in cat:
        return CHECKER_REGISTRY["OIL_GAS_EXPERIENCE"]
    if "MANPOWER" in cat or "ENGINEER" in cat:
        return CHECKER_REGISTRY["TECHNICAL_MANPOWER"]
    if "HSE" in cat or "SAFETY" in cat or "OEM" in cat or "LOCAL" in cat:
        return CHECKER_REGISTRY["HSE_SAFETY"]
    # Fallback to tender specific checker
    return TenderSpecificChecker()

__all__ = [
    "BaseChecker",
    "GSTChecker",
    "PANChecker",
    "TurnoverChecker",
    "OilGasExperienceChecker",
    "SimilarPipelineExperienceChecker",
    "TechnicalManpowerChecker",
    "TenderSpecificChecker",
    "CHECKER_REGISTRY",
    "get_checker_for_category"
]
