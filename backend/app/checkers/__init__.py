from app.checkers.base_checker import BaseChecker
from app.checkers.gst_checker import GSTChecker
from app.checkers.pan_checker import PANChecker
from app.checkers.turnover_checker import TurnoverChecker
from app.checkers.oil_gas_experience_checker import OilGasExperienceChecker
from app.checkers.similar_pipeline_checker import SimilarPipelineExperienceChecker
from app.checkers.technical_manpower_checker import TechnicalManpowerChecker
from app.checkers.tender_specific_checker import TenderSpecificChecker

# Singleton checker instances
_gst = GSTChecker()
_pan = PANChecker()
_turnover = TurnoverChecker()
_oil_gas = OilGasExperienceChecker()
_pipeline = SimilarPipelineExperienceChecker()
_manpower = TechnicalManpowerChecker()
_tender = TenderSpecificChecker()

# ── CHECKER REGISTRY ───────────────────────────────────────────────────────────
# Maps BOTH the 10 locked ML class names AND legacy internal names to checkers.
# DO NOT remove or rename any of the 10 locked ML class names below.
CHECKER_REGISTRY = {
    # ── 10 Locked ML Classification Classes ────────────────────────────────────
    "GST_TAX_COMPLIANCE":           _gst,
    "MSME_UDYAM_ELIGIBILITY":       _tender,
    "FINANCIAL_ELIGIBILITY":        _turnover,
    "EXPERIENCE_ELIGIBILITY":       _oil_gas,
    "OEM_AUTHORIZATION":            _tender,
    "BLACKLISTING_DEBARMENT":       _tender,
    "TECHNICAL_SPECIFICATION":      _tender,
    "INDUSTRY_STANDARD_COMPLIANCE": _tender,
    "SAFETY_REGULATORY_COMPLIANCE": _tender,
    "MAKE_IN_INDIA_LOCAL_CONTENT":  _tender,

    # ── Legacy / Internal Category Names (backward compat) ─────────────────────
    "GST":                          _gst,
    "PAN":                          _pan,
    "TURNOVER":                     _turnover,
    "OIL_GAS_EXPERIENCE":           _oil_gas,
    "SIMILAR_PIPELINE_EXPERIENCE":  _pipeline,
    "TECHNICAL_MANPOWER":           _manpower,
    "HSE_SAFETY":                   _tender,
    "OEM":                          _tender,
    "LOCAL_CONTENT":                _tender,
    "TENDER_SPECIFIC":              _tender,
}


def get_checker_for_category(category: str) -> BaseChecker:
    """Return the appropriate checker for a requirement category."""
    cat = (category or "").upper().strip()
    if cat in CHECKER_REGISTRY:
        return CHECKER_REGISTRY[cat]

    # Fuzzy fallback matching
    if "PIPELINE" in cat or "SIMILAR" in cat:
        return _pipeline
    if "OIL" in cat or "GAS" in cat or "EXPERIENCE" in cat:
        return _oil_gas
    if "MANPOWER" in cat or "ENGINEER" in cat or "PERSONNEL" in cat:
        return _manpower
    if "HSE" in cat or "SAFETY" in cat or "SAFETY_REGULATORY" in cat:
        return _tender
    if "OEM" in cat or "AUTHORIZ" in cat:
        return _tender
    if "LOCAL" in cat or "MAKE_IN" in cat or "INDIA" in cat:
        return _tender
    if "BLACKLIST" in cat or "DEBARR" in cat:
        return _tender
    if "MSME" in cat or "UDYAM" in cat:
        return _tender
    if "FINANCIAL" in cat or "TURNOVER" in cat:
        return _turnover
    if "GST" in cat:
        return _gst
    if "PAN" in cat or "INCOME_TAX" in cat:
        return _pan

    # Default
    return _tender


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

