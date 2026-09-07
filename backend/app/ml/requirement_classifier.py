"""
SIH26100 — scikit-learn Requirement Classifier
-------------------------------------------------
TF-IDF + LogisticRegression classifier for petroleum procurement
requirement clauses. Classifies text into one of 10 locked classes.

This is a domain-specific scikit-learn classifier trained on
petroleum pipeline procurement examples — NOT a large production model.
"""
import os
import threading
from typing import Dict, Any, List, Optional
from app.core.logging_config import logger

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

# Paths — locate authoritative model file in ml/models/
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_THIS_DIR)))
_CLASSIFIER_PATH = os.path.join(_PROJECT_ROOT, "ml", "models", "requirement_classifier.joblib")
_FALLBACK_CLASSIFIER_PATH = os.path.join(_THIS_DIR, "models", "requirement_classifier.joblib")


class RequirementClassifier:
    """
    scikit-learn domain classifier for petroleum procurement requirements.
    Uses TF-IDF vectorization + Logistic Regression.
    Models are loaded lazily on first use to avoid blocking server startup.
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
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

    def _resolve_model_path(self) -> Optional[str]:
        for p in [_CLASSIFIER_PATH, _FALLBACK_CLASSIFIER_PATH]:
            if os.path.exists(p):
                return p
        return None

    def _load_model(self) -> bool:
        """Lazily load the trained sklearn pipeline. Returns True if successful."""
        if self._loaded:
            return self._pipeline is not None

        try:
            import joblib
            target_path = self._resolve_model_path()
            if not target_path:
                self._load_error = (
                    f"Model file not found at {_CLASSIFIER_PATH}. "
                    "Run: python ml/scripts/train_requirement_classifier.py"
                )
                logger.warning(self._load_error)
                self._loaded = True
                return False

            self._pipeline = joblib.load(target_path)
            logger.info(f"RequirementClassifier loaded from {target_path}")
            self._loaded = True
            return True
        except Exception as e:
            self._load_error = f"Failed to load RequirementClassifier: {e}"
            logger.error(self._load_error)
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
                "model_ready": False,
                "error": "Empty input text"
            }

        if not self._load_model() or self._pipeline is None:
            # Fallback: keyword-based heuristic
            return self._keyword_fallback(text)

        try:
            proba = self._pipeline.predict_proba([text])[0]
            classes = self._pipeline.classes_
            pred_idx = int(proba.argmax())
            predicted_class = classes[pred_idx]
            confidence = float(round(proba[pred_idx], 4))
            all_scores = {cls: float(round(p, 4)) for cls, p in zip(classes, proba)}

            return {
                "text": text,
                "predicted_class": predicted_class,
                "confidence": confidence,
                "all_scores": all_scores,
                "classifier_type": "scikit-learn domain classifier",
                "model_ready": True
            }
        except Exception as e:
            logger.error(f"RequirementClassifier.classify error: {e}")
            return self._keyword_fallback(text)

    def classify_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Classify multiple texts in a single call."""
        return [self.classify(t) for t in texts]

    def _keyword_fallback(self, text: str) -> Dict[str, Any]:
        """
        Deterministic keyword heuristic fallback when model is unavailable.
        This ensures the API always returns a valid response for the demo.
        """
        lower = text.lower()

        if any(k in lower for k in ["gst", "gstin", "gstr", "goods and services tax"]):
            cls = "GST_TAX_COMPLIANCE"
        elif any(k in lower for k in ["msme", "udyam", "micro", "small enterprise"]):
            cls = "MSME_UDYAM_ELIGIBILITY"
        elif any(k in lower for k in ["turnover", "annual financial", "net worth", "solvency", "crore", "itr"]):
            cls = "FINANCIAL_ELIGIBILITY"
        elif any(k in lower for k in ["experience", "pipeline project", "completed", "executed", "commissioned", "epc"]):
            cls = "EXPERIENCE_ELIGIBILITY"
        elif any(k in lower for k in ["oem", "manufacturer authorization", "maf", "authorized dealer"]):
            cls = "OEM_AUTHORIZATION"
        elif any(k in lower for k in ["blacklist", "debarr", "debarment", "suspension", "non-conviction", "affidavit"]):
            cls = "BLACKLISTING_DEBARMENT"
        elif any(k in lower for k in ["local content", "make in india", "mii", "indigenous content", "dpiit"]):
            cls = "MAKE_IN_INDIA_LOCAL_CONTENT"
        elif any(k in lower for k in ["hse", "safety", "iso 45001", "iso 14001", "health and safety", "oisd"]):
            cls = "SAFETY_REGULATORY_COMPLIANCE"
        elif any(k in lower for k in ["api 6d", "api 5l", "asme", "api 1104", "nace", "oisd", "bis standard", "is 3589"]):
            cls = "INDUSTRY_STANDARD_COMPLIANCE"
        else:
            cls = "TECHNICAL_SPECIFICATION"

        return {
            "text": text,
            "predicted_class": cls,
            "confidence": 0.75,
            "all_scores": {cls: 0.75},
            "classifier_type": "scikit-learn domain classifier (keyword fallback)",
            "model_ready": False
        }

    def get_info(self) -> Dict[str, Any]:
        """Return metadata about the classifier for the frontend info banner."""
        ready = self._load_model() and self._pipeline is not None
        return {
            "model_type": "scikit-learn domain classifier",
            "algorithm": "TF-IDF Vectorizer + Logistic Regression",
            "classes": REQUIREMENT_CLASSES,
            "num_classes": len(REQUIREMENT_CLASSES),
            "model_ready": ready,
            "model_path": _CLASSIFIER_PATH if ready else None,
            "load_error": self._load_error,
            "description": (
                "Lightweight scikit-learn classifier trained on petroleum "
                "procurement requirement examples. Not a large production model."
            )
        }


# Singleton instance
requirement_classifier = RequirementClassifier.get_instance()
