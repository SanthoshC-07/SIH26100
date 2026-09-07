"""
Petroleum Requirement Detector & Clause Classifier
Ministry of Petroleum & Natural Gas - Petroleum & Natural Gas Pipeline Procurement
"""
import re
from typing import Dict, Any, Tuple, Optional
from app.nlp.vocabulary import PetroleumVocabulary
from app.nlp.text_normalizer import TextNormalizer

class RequirementDetector:
    """
    Classifies tender clauses into REQUIREMENT, INFORMATIONAL, SCOPE,
    TECHNICAL_SPECIFICATION, COMMERCIAL, or OTHER, and identifies
    the primary Petroleum requirement category.
    """

    # Strong obligation / modal requirement indicators
    REQUIREMENT_SIGNALS = [
        "shall", "must", "required", "minimum", "at least", "eligible",
        "eligibility", "should have", "submit", "submission of", "possess",
        "proven experience", "completed", "valid", "not less than",
        "not more than", "mandatory", "criteria", "qualification",
        "prior experience", "annual turnover", "key personnel"
    ]

    # Informational / Scope indicators
    SCOPE_SIGNALS = [
        "scope of work", "scope of supply", "the project involves",
        "brief description of project", "geographical location",
        "terminal facility", "pipeline route"
    ]

    TECH_SPEC_SIGNALS = [
        "technical specification", "wall thickness", "design pressure",
        "material grade", "api 5l x70", "coating specification",
        "3lpe coating", "hydrostatic test pressure", "design temperature"
    ]

    COMMERCIAL_SIGNALS = [
        "earnest money deposit", "emd", "bid security", "payment terms",
        "price schedule", "taxes and duties", "liquidated damages",
        "performance bank guarantee", "pbg", "contract period"
    ]

    @classmethod
    def detect_clause_type(cls, clause_text: str) -> Tuple[str, float]:
        """
        Classifies clause type with confidence score.
        Returns: (clause_type, confidence)
        """
        lower = clause_text.lower()

        # Check Requirement Signals
        req_score = sum(1 for s in cls.REQUIREMENT_SIGNALS if s in lower)
        
        # Check Scope Signals
        scope_score = sum(1 for s in cls.SCOPE_SIGNALS if s in lower)

        # Check Tech Spec Signals
        tech_score = sum(1 for s in cls.TECH_SPEC_SIGNALS if s in lower)

        # Check Commercial Signals
        comm_score = sum(1 for s in cls.COMMERCIAL_SIGNALS if s in lower)

        # Disambiguation logic
        if req_score >= 2 or (req_score >= 1 and any(cat in lower for cat in ["turnover", "experience", "gst", "pan", "manpower", "iso 45001", "local content"])):
            confidence = min(0.98, 0.75 + (req_score * 0.06))
            return "REQUIREMENT", round(confidence, 2)

        if scope_score >= 1 and req_score == 0:
            return "SCOPE", 0.92

        if tech_score >= 2 and req_score == 0:
            return "TECHNICAL_SPECIFICATION", 0.90

        if comm_score >= 1 and req_score == 0:
            return "COMMERCIAL", 0.88

        if req_score == 1:
            return "REQUIREMENT", 0.82

        if len(clause_text) < 60:
            return "INFORMATIONAL", 0.75

        return "OTHER", 0.70

    @classmethod
    def categorize_petroleum_requirement(cls, clause_text: str) -> Tuple[Optional[str], Optional[str], float]:
        """
        Determines the Primary Petroleum Category and Subtype.
        Returns: (primary_category, subtype, confidence)
        """
        lower = clause_text.lower()

        # 1. GST
        if re.search(r"\b(?:gst|gstin|goods and services tax)\b", lower):
            return "GST", None, 0.98

        # 2. PAN / Income Tax
        if re.search(r"\b(?:pan|permanent account number|itr|income tax return)\b", lower):
            return "PAN", None, 0.98

        # 3. Turnover
        if re.search(r"\b(?:turnover|annual financial turnover|annual turnover|audited balance sheet)\b", lower):
            return "TURNOVER", None, 0.97

        # 4. Similar Pipeline Experience (Check this before generic Oil & Gas)
        if ("pipeline" in lower and any(w in lower for w in ["km", "length", "diameter", "cross-country", "transmission", "similar", "gas pipeline", "oil pipeline", "constructed", "commissioned"])) or "similar pipeline" in lower:
            return "SIMILAR_PIPELINE_EXPERIENCE", None, 0.96

        # 5. Oil & Gas Sector Experience
        if any(w in lower for w in ["oil & gas", "oil and gas", "petroleum", "hydrocarbon", "refinery", "petrochemical", "cgd"]):
            return "OIL_GAS_EXPERIENCE", None, 0.95

        # 6. Technical Manpower / Personnel
        if any(w in lower for w in ["manpower", "personnel", "engineer", "engineers", "technical staff", "welding inspector", "ndt level", "b.tech", "cvs"]):
            return "TECHNICAL_MANPOWER", None, 0.96

        # 7. Tender Specific: HSE
        if any(w in lower for w in ["hse", "safety", "iso 45001", "iso 14001", "health and safety", "environment management", "safety policy"]):
            return "TENDER_SPECIFIC", "HSE_SAFETY", 0.95

        # 7. Tender Specific: OEM
        if any(w in lower for w in ["oem", "manufacturer authorization", "maf", "line pipe manufacturer", "authorized dealer"]):
            return "TENDER_SPECIFIC", "OEM_AUTHORIZATION", 0.94

        # 7. Tender Specific: Local Content
        if any(w in lower for w in ["local content", "make in india", "mii", "indigenous content", "class-i", "class-ii"]):
            return "TENDER_SPECIFIC", "LOCAL_CONTENT", 0.95

        return None, None, 0.60
