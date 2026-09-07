"""
Petroleum Requirement Structurer
Ministry of Petroleum & Natural Gas - Petroleum & Natural Gas Pipeline Procurement
"""
import re
from typing import Dict, Any, Optional
from app.nlp.text_normalizer import TextNormalizer
from app.nlp.vocabulary import PetroleumVocabulary

class RequirementStructurer:
    """
    Converts natural-language requirement clauses into structured JSON constraint representations.
    """

    WORD_TO_NUM = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
    }

    @classmethod
    def structure_requirement(cls, category: str, subtype: Optional[str], clause_text: str) -> Dict[str, Any]:
        """
        Structures constraints from raw clause text into domain-specific JSON.
        """
        lower = clause_text.lower()
        mandatory = not bool(re.search(r"\b(?:optional|preferable|desirable)\b", lower))

        if category == "SIMILAR_PIPELINE_EXPERIENCE":
            return cls._structure_similar_pipeline(lower, clause_text, mandatory)
        elif category == "TURNOVER":
            return cls._structure_turnover(lower, clause_text, mandatory)
        elif category == "OIL_GAS_EXPERIENCE":
            return cls._structure_oil_gas_exp(lower, clause_text, mandatory)
        elif category == "TECHNICAL_MANPOWER":
            return cls._structure_manpower(lower, clause_text, mandatory)
        elif category == "GST":
            return {
                "category": "GST",
                "mandatory": mandatory,
                "status_required": "ACTIVE",
                "evidence_required": ["GST_REGISTRATION_CERTIFICATE", "LATEST_GSTR_3B_FILING"],
                "confidence": 0.98
            }
        elif category == "PAN":
            return {
                "category": "PAN",
                "mandatory": mandatory,
                "status_required": "VALID",
                "evidence_required": ["PAN_CARD", "ITR_ACKNOWLEDGEMENT"],
                "confidence": 0.98
            }
        elif category == "TENDER_SPECIFIC":
            return cls._structure_tender_specific(subtype, lower, clause_text, mandatory)

        return {
            "category": category,
            "mandatory": mandatory,
            "raw_text": clause_text,
            "confidence": 0.85
        }

    @classmethod
    def _structure_similar_pipeline(cls, lower: str, raw_text: str, mandatory: bool) -> Dict[str, Any]:
        # Extract pipeline type
        pipeline_type = "NATURAL_GAS"
        if "crude" in lower or "oil pipeline" in lower:
            pipeline_type = "CRUDE_OIL"
        elif "product" in lower:
            pipeline_type = "PETROLEUM_PRODUCT"

        # Extract KM length
        km = TextNormalizer.parse_distance_km(raw_text) or 100.0

        # Extract Project Count
        m_count = re.search(r"\b(?:at least|minimum(?:\s+of)?\s+)?([0-9]+|one|two|three|four|five|six|seven|eight|nine|ten)\s+(?:[a-z\s]{0,35})?(?:pipeline projects?|projects?|works?|contracts?)\b", lower)
        count = 1
        if m_count:
            token = m_count.group(1).lower()
            count = int(token) if token.isdigit() else cls.WORD_TO_NUM.get(token, 1)


        # Extract Lookback years
        m_lookback = re.search(r"\b(?:last|past|preceding)?\s*([0-9]+|one|two|three|four|five|six|seven|eight|nine|ten)\s*(?:years|yrs)\b", lower)
        lookback = 7
        if m_lookback:
            token = m_lookback.group(1).lower()
            lookback = int(token) if token.isdigit() else cls.WORD_TO_NUM.get(token, 7)


        # Extract Diameter if present
        dia = TextNormalizer.parse_diameter_inch(raw_text)

        return {
            "category": "SIMILAR_PIPELINE_EXPERIENCE",
            "mandatory": mandatory,
            "minimum_project_count": count,
            "pipeline_type": pipeline_type,
            "minimum_pipeline_length_km": km,
            "minimum_diameter_inch": dia,
            "lookback_years": lookback,
            "completion_required": True,
            "confidence": 0.96
        }

    @classmethod
    def _structure_turnover(cls, lower: str, raw_text: str, mandatory: bool) -> Dict[str, Any]:
        # Extract monetary threshold
        curr_tuple = TextNormalizer.parse_currency_amount(raw_text)
        threshold_cr = 10.0
        unit = "CRORE_INR"
        comparison = ">="

        if curr_tuple:
            amount_inr, _ = curr_tuple
            threshold_cr = amount_inr / 10000000.0
        else:
            # Match plain number before Crore
            m_num = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(?:cr|crore)", lower)
            if m_num:
                threshold_cr = float(m_num.group(1))

        # Financial year count
        m_fy = re.search(r"\b(?:last|past|preceding)?\s*([0-9]+|three|four|five)\s*(?:financial years|years|fys)\b", lower)
        fy_count = 3
        if m_fy:
            token = m_fy.group(1).lower()
            fy_count = int(token) if token.isdigit() else cls.WORD_TO_NUM.get(token, 3)

        return {
            "category": "TURNOVER",
            "mandatory": mandatory,
            "threshold": threshold_cr,
            "unit": unit,
            "comparison": comparison,
            "financial_year_count": fy_count,
            "confidence": 0.97
        }

    @classmethod
    def _structure_oil_gas_exp(cls, lower: str, raw_text: str, mandatory: bool) -> Dict[str, Any]:
        m_yrs = re.search(r"\b(?:minimum|at least)?\s*([0-9]+|five|seven|ten)\s*years\b", lower)
        min_years = 5.0
        if m_yrs:
            token = m_yrs.group(1).lower()
            min_years = float(token) if token.isdigit() else float(cls.WORD_TO_NUM.get(token, 5))

        return {
            "category": "OIL_GAS_EXPERIENCE",
            "mandatory": mandatory,
            "minimum_years": min_years,
            "sector": "OIL_AND_GAS",
            "confidence": 0.95
        }

    @classmethod
    def _structure_manpower(cls, lower: str, raw_text: str, mandatory: bool) -> Dict[str, Any]:
        m_count = re.search(r"\b(?:minimum|at least)?\s*([0-9]+|five|three|four)\s*(?:qualified\s+)?(?:pipeline engineers?|engineers?|personnel|staff)\b", lower)
        min_count = 5
        if m_count:
            token = m_count.group(1).lower()
            min_count = int(token) if token.isdigit() else cls.WORD_TO_NUM.get(token, 5)

        m_exp = re.search(r"\b([0-9]+)\s*years\b", lower)
        min_exp = float(m_exp.group(1)) if m_exp else 8.0

        qualification = "B.Tech / B.E. Mechanical / Pipeline"
        if "civil" in lower:
            qualification = "B.Tech / B.E. Civil"

        return {
            "category": "TECHNICAL_MANPOWER",
            "mandatory": mandatory,
            "minimum_personnel": min_count,
            "qualification": qualification,
            "minimum_experience_years": min_exp,
            "confidence": 0.96
        }

    @classmethod
    def _structure_tender_specific(cls, subtype: Optional[str], lower: str, raw_text: str, mandatory: bool) -> Dict[str, Any]:
        if subtype == "HSE_SAFETY" or "iso 45001" in lower or "hse" in lower:
            certs = []
            if "iso 45001" in lower or "ohsas" in lower or "safety" in lower:
                certs.append("ISO 45001")
            if "iso 14001" in lower or "environment" in lower:
                certs.append("ISO 14001")
            if not certs:
                certs = ["ISO 45001", "ISO 14001"]

            return {
                "category": "TENDER_SPECIFIC",
                "subtype": "HSE_SAFETY",
                "mandatory": mandatory,
                "required_certifications": certs,
                "confidence": 0.95
            }
        elif subtype == "LOCAL_CONTENT" or "local content" in lower or "make in india" in lower:
            m_pct = re.search(r"([0-9]{1,3})\s*%", lower)
            pct = float(m_pct.group(1)) if m_pct else 50.0
            return {
                "category": "TENDER_SPECIFIC",
                "subtype": "LOCAL_CONTENT",
                "mandatory": mandatory,
                "minimum_percentage": pct,
                "unit": "%",
                "confidence": 0.95
            }
        elif subtype == "OEM_AUTHORIZATION" or "oem" in lower:
            return {
                "category": "TENDER_SPECIFIC",
                "subtype": "OEM_AUTHORIZATION",
                "mandatory": mandatory,
                "authorization_form_required": "MAF",
                "confidence": 0.94
            }

        return {
            "category": "TENDER_SPECIFIC",
            "subtype": subtype or "GENERAL",
            "mandatory": mandatory,
            "confidence": 0.90
        }
