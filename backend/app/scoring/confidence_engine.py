from typing import Dict, Any, Optional
from app.core.config import settings

class ConfidenceEngine:
    """
    SIH26100 Phase 3: Hybrid Confidence Scoring & Gating Engine
    Computes explainable, multi-signal confidence scores across rule determinism,
    semantic NLP signals, OCR/entity extraction quality, and cross-document consistency.
    """

    # Configurable prototype scoring weights
    DEFAULT_WEIGHTS = {
        "rule_confidence": 0.40,
        "semantic_confidence": 0.30,
        "evidence_confidence": 0.20,
        "consistency_confidence": 0.10
    }

    # Configurable semantic threshold gates
    HIGH_SEMANTIC_THRESHOLD = 0.85
    MEDIUM_SEMANTIC_THRESHOLD = 0.70

    # Configurable overall confidence gating thresholds
    HIGH_CONFIDENCE_GATE = 0.85
    MEDIUM_CONFIDENCE_GATE = 0.70

    @classmethod
    def calculate_confidence(
        cls,
        rule_confidence: float = 0.95,
        semantic_confidence: float = 0.90,
        evidence_confidence: float = 0.90,
        consistency_confidence: float = 0.95,
        custom_weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Calculates composite overall confidence score with full component breakdown.
        """
        weights = custom_weights or cls.DEFAULT_WEIGHTS

        r_conf = max(0.0, min(1.0, float(rule_confidence)))
        s_conf = max(0.0, min(1.0, float(semantic_confidence)))
        e_conf = max(0.0, min(1.0, float(evidence_confidence)))
        c_conf = max(0.0, min(1.0, float(consistency_confidence)))

        overall = (
            r_conf * weights.get("rule_confidence", 0.40) +
            s_conf * weights.get("semantic_confidence", 0.30) +
            e_conf * weights.get("evidence_confidence", 0.20) +
            c_conf * weights.get("consistency_confidence", 0.10)
        )
        overall = round(max(0.0, min(1.0, overall)), 3)

        return {
            "overall_confidence": overall,
            "rule_confidence": r_conf,
            "semantic_confidence": s_conf,
            "evidence_confidence": e_conf,
            "consistency_confidence": c_conf,
            "weights_applied": weights,
            "confidence_gate": cls.evaluate_gate(overall)
        }

    @classmethod
    def evaluate_gate(cls, overall_confidence: float) -> str:
        """
        Maps confidence score to gate level: HIGH, MEDIUM, LOW.
        """
        if overall_confidence >= cls.HIGH_CONFIDENCE_GATE:
            return "HIGH"
        elif overall_confidence >= cls.MEDIUM_CONFIDENCE_GATE:
            return "MEDIUM"
        return "LOW"

    @classmethod
    def apply_confidence_policy(
        cls,
        provisional_status: str,
        overall_confidence: float,
        semantic_score: Optional[float] = None,
        has_missing_evidence: bool = False,
        has_contradictions: bool = False,
        is_mandatory: bool = True
    ) -> Dict[str, Any]:
        """
        Enforces statutory confidence policy:
        - Never auto-PASS on missing evidence, contradictions, low semantic match, or low confidence.
        - Uncertainty is routed to REVIEW.
        """
        gate = cls.evaluate_gate(overall_confidence)
        final_status = provisional_status
        gating_rationale = []

        if has_missing_evidence:
            final_status = "INSUFFICIENT"
            gating_rationale.append("Required compliance evidence is missing or incomplete.")
        elif has_contradictions:
            final_status = "REVIEW"
            gating_rationale.append("Contradictory information identified across submitted documents.")
        elif semantic_score is not None and semantic_score < cls.MEDIUM_SEMANTIC_THRESHOLD:
            final_status = "REVIEW" if not is_mandatory else ("FAIL" if semantic_score < 0.50 else "REVIEW")
            gating_rationale.append(f"Semantic similarity score ({semantic_score:.2f}) is below threshold ({cls.MEDIUM_SEMANTIC_THRESHOLD:.2f}).")
        elif gate == "MEDIUM" and provisional_status == "PASS":
            final_status = "REVIEW"
            gating_rationale.append(f"Medium confidence ({overall_confidence:.2f}) requires Procurement Officer verification.")
        elif gate == "LOW":
            final_status = "REVIEW" if provisional_status != "FAIL" else "FAIL"
            gating_rationale.append(f"Low confidence ({overall_confidence:.2f}) requires manual evaluation.")

        return {
            "status": final_status,
            "confidence": overall_confidence,
            "gate": gate,
            "gating_applied": final_status != provisional_status,
            "gating_rationale": " ".join(gating_rationale) if gating_rationale else "Confidence passed statutory gating threshold."
        }
