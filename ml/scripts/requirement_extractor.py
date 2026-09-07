"""
SIH26100 — Authoritative Requirement Extractor Module
------------------------------------------------------
Extracts and structures requirements from petroleum tender document clauses
using the TF-IDF + Logistic Regression requirement classifier and domain heuristics.

Authoritative Path:
    ml/scripts/requirement_extractor.py
"""
import re
import json
import os
from typing import List, Dict, Any, Optional

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_ML_DIR = os.path.dirname(_THIS_DIR)
_TERMS_PATH = os.path.join(_ML_DIR, "datasets", "petroleum_terms.json")

try:
    from ml.scripts.requirement_classifier import requirement_classifier, REQUIREMENT_CLASSES
except ImportError:
    from requirement_classifier import requirement_classifier, REQUIREMENT_CLASSES


class RequirementExtractor:
    """
    Extracts, classifies, and structures petroleum pipeline procurement requirements.
    """

    def __init__(self, terms_path: Optional[str] = None):
        self.terms_path = terms_path or _TERMS_PATH
        self.terms = self._load_terms()

    def _load_terms(self) -> Dict[str, Any]:
        if os.path.exists(self.terms_path):
            try:
                with open(self.terms_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def extract_from_clause(self, clause_text: str, clause_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Extracts structured metadata from a single tender requirement clause.
        """
        classification = requirement_classifier.classify(clause_text)
        predicted_class = classification.get("predicted_class", "TECHNICAL_SPECIFICATION")
        confidence = classification.get("confidence", 0.0)

        # Detect mandatory status
        mandatory = bool(re.search(r"\b(shall|must|mandatory|required|compulsory|strictly)\b", clause_text, re.I))

        # Detect numeric threshold if applicable
        threshold, threshold_unit = self._extract_threshold(clause_text, predicted_class)

        # Map to required evidence types
        evidence_types = self._map_evidence_types(predicted_class)

        return {
            "clause_id": clause_id or "REQ-EXTRACTED",
            "clause_text": clause_text,
            "category": predicted_class,
            "confidence": confidence,
            "mandatory": mandatory,
            "threshold": threshold,
            "threshold_unit": threshold_unit,
            "evidence_types": evidence_types,
            "all_scores": classification.get("all_scores", {})
        }

    def extract_from_document(self, text: str) -> List[Dict[str, Any]]:
        """
        Splits text into clauses and extracts all requirements.
        """
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if not paragraphs:
            paragraphs = [p.strip() for p in text.split("\n") if p.strip()]

        results = []
        for i, p in enumerate(paragraphs, 1):
            if len(p) < 15:
                continue
            req = self.extract_from_clause(p, f"REQ-{i:03d}")
            results.append(req)
        return results

    def _extract_threshold(self, text: str, category: str) -> tuple:
        if category == "FINANCIAL_ELIGIBILITY":
            m = re.search(r"(?:inr|rs\.?|₹)?\s*([0-9]+(?:\.[0-9]+)?)\s*(crore|cr|lakh|lac)s?", text, re.I)
            if m:
                val = float(m.group(1))
                unit = m.group(2).upper()
                mult = 10000000.0 if "CR" in unit else 100000.0
                return val * mult, "INR"
        elif category == "EXPERIENCE_ELIGIBILITY":
            m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(?:km|kms|kilometer|kilometre)s?", text, re.I)
            if m:
                return float(m.group(1)), "KM"
            m2 = re.search(r"([0-9]+)\s*(?:years?|yrs?)", text, re.I)
            if m2:
                return float(m2.group(1)), "YEARS"
        elif category == "MAKE_IN_INDIA_LOCAL_CONTENT":
            m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*%", text)
            if m:
                return float(m.group(1)), "PERCENT"
        return None, None

    def _map_evidence_types(self, category: str) -> List[str]:
        mapping = {
            "GST_TAX_COMPLIANCE": ["GST_REGISTRATION_CERTIFICATE", "LATEST_GSTR_3B_FILING"],
            "MSME_UDYAM_ELIGIBILITY": ["UDYAM_REGISTRATION_CERTIFICATE"],
            "FINANCIAL_ELIGIBILITY": ["AUDITED_BALANCE_SHEET", "CA_TURNOVER_CERTIFICATE"],
            "EXPERIENCE_ELIGIBILITY": ["CLIENT_COMPLETION_CERTIFICATE", "PURCHASE_ORDER"],
            "OEM_AUTHORIZATION": ["MANUFACTURER_AUTHORIZATION_FORM", "OEM_WARRANTY_LETTER"],
            "BLACKLISTING_DEBARMENT": ["NON_BLACKLISTING_AFFIDAVIT"],
            "TECHNICAL_SPECIFICATION": ["TECHNICAL_DATA_SHEET", "DRAWING_COMPLIANCE_SCHEDULE"],
            "INDUSTRY_STANDARD_COMPLIANCE": ["API_SPEC_CERTIFICATE", "ASME_COMPLIANCE_REPORT"],
            "SAFETY_REGULATORY_COMPLIANCE": ["ISO_45001_CERTIFICATE", "HSE_POLICY_DECLARATION"],
            "MAKE_IN_INDIA_LOCAL_CONTENT": ["LOCAL_CONTENT_DECLARATION", "CA_LOCAL_CONTENT_CERTIFICATE"]
        }
        return mapping.get(category, ["GENERAL_SUPPORTING_DOCUMENT"])


requirement_extractor = RequirementExtractor()
