"""
SIH26100 — Authoritative Requirement Classifier Inference Module
-----------------------------------------------------------------
TF-IDF + LogisticRegression domain classifier for petroleum procurement
requirement clauses. Classifies text into one of 10 locked classes.

Authoritative Path:
    ml/scripts/requirement_classifier.py
"""
import os
import sys
import threading
from typing import Dict, Any, List, Optional

# The 10 locked requirement classes — DO NOT ADD, REMOVE, OR RENAME
REQUIREMENT_CLASSES = [
    "GST_TAX_COMPLIANCE",
    "MSME_UDYAM_ELIGIBILITY",
    "FINANCIAL_ELIGIBILITY",
    "EXPERIENCE_ELIGIBILITY",
    "OEM_AUTHORIZATION",
    "BLACKLISTING_DEBARMENT",
    "TECHNICAL_SPECIFICATION",
    "INDUSTRY_STANDARD_COMPLIANCE",
    "SAFETY_REGULATORY_COMPLIANCE",
    "MAKE_IN_INDIA_LOCAL_CONTENT",
]

# Paths — locate authoritative model file
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_ML_DIR = os.path.dirname(_THIS_DIR)
_MODELS_DIR = os.path.join(_ML_DIR, "models")
_CLASSIFIER_PATH = os.path.join(_MODELS_DIR, "requirement_classifier.joblib")


class RequirementClassifier:
    """
    Authoritative scikit-learn domain classifier for petroleum procurement requirements.
    Uses TF-IDF vectorization + Logistic Regression.
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(self, model_path: Optional[str] = None):
        self._model_path = model_path or _CLASSIFIER_PATH
        self._pipeline = None
        self._loaded = False
        self._load_error: Optional[str] = None

    @classmethod
    def get_instance(cls) -> "RequirementClassifier":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _load_model(self) -> bool:
        """Lazily load the trained sklearn pipeline. Returns True if successful."""
        if self._loaded:
            return self._pipeline is not None

        try:
            import joblib
            if not os.path.exists(self._model_path):
                self._load_error = (
                    f"Model file not found at {self._model_path}. "
                    "Run: python ml/scripts/train_requirement_classifier.py"
                )
                self._loaded = True
                return False

            self._pipeline = joblib.load(self._model_path)
            self._loaded = True
            return True
        except Exception as e:
            self._load_error = f"Failed to load RequirementClassifier: {e}"
            self._loaded = True
            return False

    @property
    def is_ready(self) -> bool:
        return self._load_model()

    def classify(self, text: str) -> Dict[str, Any]:
        """
        Classify a requirement clause text into one of 10 locked classes.

        Returns:
            {
                "text": str,
                "predicted_class": str,       # one of REQUIREMENT_CLASSES
                "confidence": float,           # 0.0 – 1.0
                "all_scores": {class: prob},   # full probability distribution
                "classifier_type": str,
                "model_ready": bool
            }
        """
        if not text or not text.strip():
            return {
                "text": text,
                "predicted_class": "TECHNICAL_SPECIFICATION",
                "confidence": 0.0,
                "all_scores": {},
                "classifier_type": "scikit-learn domain classifier",
                "model_ready": self.is_ready,
                "error": "Empty input text"
            }

        if not self._load_model() or self._pipeline is None:
            # Fallback to rule-based keyword heuristic
            fallback_class, fallback_conf = self._rule_based_fallback(text)
            return {
                "text": text,
                "predicted_class": fallback_class,
                "confidence": fallback_conf,
                "all_scores": {fallback_class: fallback_conf},
                "classifier_type": "rule-based heuristic (model unavailable)",
                "model_ready": False,
                "load_error": self._load_error
            }

        try:
            proba = self._pipeline.predict_proba([text])[0]
            classes = self._pipeline.classes_
            pred_idx = proba.argmax()
            predicted_class = classes[pred_idx]
            confidence = float(proba[pred_idx])

            all_scores = {
                cls_name: round(float(prob), 4)
                for cls_name, prob in zip(classes, proba)
            }

            return {
                "text": text,
                "predicted_class": predicted_class,
                "confidence": round(confidence, 4),
                "all_scores": all_scores,
                "classifier_type": "scikit-learn domain classifier",
                "model_ready": True
            }
        except Exception as e:
            fallback_class, fallback_conf = self._rule_based_fallback(text)
            return {
                "text": text,
                "predicted_class": fallback_class,
                "confidence": fallback_conf,
                "all_scores": {fallback_class: fallback_conf},
                "classifier_type": "rule-based fallback (inference error)",
                "model_ready": True,
                "error": str(e)
            }

    def classify_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Classify a list of requirement texts efficiently."""
        if not texts:
            return []
        return [self.classify(t) for t in texts]

    def _rule_based_fallback(self, text: str) -> tuple:
        """Keyword heuristic fallback when model is not loaded."""
        lower = text.lower()
        if any(k in lower for k in ["gst", "gstin", "gstr"]):
            return "GST_TAX_COMPLIANCE", 0.90
        if any(k in lower for k in ["udyam", "msme", "micro enterprise", "small enterprise"]):
            return "MSME_UDYAM_ELIGIBILITY", 0.90
        if any(k in lower for k in ["turnover", "net worth", "crore", "solvency", "balance sheet"]):
            return "FINANCIAL_ELIGIBILITY", 0.85
        if any(k in lower for k in ["experience", "executed", "completed", "similar project", "pipeline laying"]):
            return "EXPERIENCE_ELIGIBILITY", 0.85
        if any(k in lower for k in ["oem", "manufacturer authorization", "maf", "authorized dealer"]):
            return "OEM_AUTHORIZATION", 0.90
        if any(k in lower for k in ["blacklist", "debarred", "debarment", "holiday list", "non-blacklisting"]):
            return "BLACKLISTING_DEBARMENT", 0.90
        if any(k in lower for k in ["api 6d", "api 5l", "api 1104", "asme b31", "oisd", "iso 9001"]):
            return "INDUSTRY_STANDARD_COMPLIANCE", 0.85
        if any(k in lower for k in ["safety", "hse", "iso 45001", "iso 14001", "osha", "hazard"]):
            return "SAFETY_REGULATORY_COMPLIANCE", 0.85
        if any(k in lower for k in ["make in india", "local content", "indigenous", "domestic value addition"]):
            return "MAKE_IN_INDIA_LOCAL_CONTENT", 0.90
        return "TECHNICAL_SPECIFICATION", 0.60

    def get_info(self) -> Dict[str, Any]:
        """Return model metadata for status endpoints."""
        ready = self.is_ready
        return {
            "name": "Petroleum Procurement Requirement Classifier",
            "type": "scikit-learn domain classifier",
            "model_path": self._model_path,
            "classes": REQUIREMENT_CLASSES,
            "num_classes": len(REQUIREMENT_CLASSES),
            "ready": ready,
            "load_error": self._load_error
        }


# Module singleton
requirement_classifier = RequirementClassifier.get_instance()
