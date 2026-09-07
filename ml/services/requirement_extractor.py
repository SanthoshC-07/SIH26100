import os
import sys
from typing import Dict, Any, Optional, List, Tuple

# Ensure project root in sys.path
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_THIS_DIR))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

try:
    from ml.services.requirement_llm import requirement_llm_service
    from ml.services.requirement_regex import regex_requirement_extractor
except ImportError:
    from requirement_llm import requirement_llm_service
    from requirement_regex import regex_requirement_extractor

try:
    from ml.scripts.requirement_classifier import requirement_classifier
except ImportError:
    try:
        from app.ml.requirement_classifier import requirement_classifier
    except ImportError:
        requirement_classifier = None


class UnifiedRequirementExtractor:
    """
    Three-Stage Pipeline for Petroleum Procurement Requirement Extraction:
    1. First: LLM (NVIDIA NIM LLaMA 3.2 90B Vision) + Regex Numerical Extractor
    2. Next: Domain Structural Logic & Semantic Entity Parser
    3. Last: ML Domain Classifier (TF-IDF + Logistic Regression) for Locked Category Validation
    """

    def __init__(self):
        self.llm_service = requirement_llm_service
        self.regex_service = regex_requirement_extractor
        self.ml_classifier = requirement_classifier

    def extract(self, requirement_text: str) -> Dict[str, Any]:
        """
        Three-Stage Requirement Extraction Pipeline:
        1. First: Try LLM (NVIDIA NIM LLaMA 3.2 90B Vision) + Deterministic Regex Extraction.
        2. Next: Try Domain Structural Logic (rule-based semantic backfill).
        3. Last: Apply ML Domain Classifier (TF-IDF + Logistic Regression) for category validation & scoring.
        """
        if not requirement_text or not requirement_text.strip():
            return {
                "requirement_text": "",
                "category": "TECHNICAL_SPECIFICATION",
                "threshold": None,
                "unit": None,
                "value": None,
                "minimum_value": None,
                "maximum_value": None,
                "currency": None,
                "percentage": None,
                "count": None,
                "time_period_years": None,
                "date": None,
                "project_type": None,
                "sector": None,
                "diameter_inch": None,
                "length_km": None,
                "experience_years": None,
                "required_count": None,
                "role": None,
                "qualification": None,
                "scope": None,
                "entities": [],
                "confidence": 0.0,
                "extraction_method": "EMPTY_INPUT",
                "status": "REVIEW"
            }

        # ---------------------------------------------------------
        # STAGE 1: First Try LLM Extraction + Deterministic Regex
        # ---------------------------------------------------------
        llm_result = self.llm_service.extract_requirement(requirement_text)
        regex_result = self.regex_service.extract_deterministic_entities(requirement_text)

        # ---------------------------------------------------------
        # STAGE 2: Next Try Domain Structural Logic & Regex Backfill
        # ---------------------------------------------------------
        fused = dict(llm_result)
        fused["entities"] = list(llm_result.get("entities", []))
        method_used = llm_result.get("extraction_method", "LLM_EXTRACTION")
        fallback_triggered = False

        # Backfill numeric and structural fields from Regex
        data_fields = [
            "threshold", "unit", "value", "minimum_value", "maximum_value",
            "currency", "percentage", "count", "date",
            "time_period_years", "diameter_inch", "length_km",
            "experience_years", "required_count"
        ]

        for field in data_fields:
            if fused.get(field) is None and regex_result.get(field) is not None:
                fused[field] = regex_result[field]
                fallback_triggered = True

        # Backfill domain metadata
        for str_field in ["project_type", "sector", "role", "qualification", "scope"]:
            if not fused.get(str_field) and regex_result.get(str_field):
                fused[str_field] = regex_result[str_field]

        # Merge unique extracted entities
        existing_entities = set(fused.get("entities", []))
        for ent in regex_result.get("entities", []):
            if ent not in existing_entities:
                fused.setdefault("entities", []).append(ent)
                existing_entities.add(ent)

        if fallback_triggered and method_used in ["LLM_EXTRACTION", "NVIDIA_NIM_LLM"]:
            fused["extraction_method"] = "LLM_WITH_REGEX_FALLBACK"
        elif method_used not in ["LLM_EXTRACTION", "NVIDIA_NIM_LLM"] and fallback_triggered:
            fused["extraction_method"] = "REGEX_FALLBACK"

        # ---------------------------------------------------------
        # STAGE 3: Last Add ML Classifier (Category Validation & Probabilities)
        # ---------------------------------------------------------
        if self.ml_classifier:
            try:
                ml_res = self.ml_classifier.classify(requirement_text)
                ml_class = ml_res.get("predicted_class")
                ml_conf = ml_res.get("confidence", 0.0)
                
                # If category was empty or default, or ML confidence is strong, harmonize category
                if not fused.get("category") or fused.get("category") == "TECHNICAL_SPECIFICATION":
                    if ml_class:
                        fused["category"] = ml_class
                
                fused["ml_predicted_class"] = ml_class
                fused["ml_confidence"] = ml_conf
                fused["ml_scores"] = ml_res.get("all_scores", {})
            except Exception:
                pass

        # ---------------------------------------------------------
        # Confidence Assessment & Readiness Status
        # ---------------------------------------------------------
        has_essential_data = bool(
            fused.get("minimum_value") is not None or
            fused.get("threshold") is not None or
            fused.get("experience_years") is not None or
            fused.get("length_km") is not None or
            fused.get("required_count") is not None or
            fused.get("percentage") is not None or
            len(fused.get("entities", [])) > 0
        )

        confidence = fused.get("confidence", 0.70)
        if fallback_triggered:
            confidence = max(confidence, 0.85)

        fused["confidence"] = round(confidence, 3)
        fused["status"] = "VERIFICATION_READY" if has_essential_data and confidence >= 0.50 else "REVIEW"

        return fused


unified_requirement_extractor = UnifiedRequirementExtractor()

