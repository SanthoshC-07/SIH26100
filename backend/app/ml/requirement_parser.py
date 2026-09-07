import re
from typing import List, Dict, Any, Optional

class TenderRequirementParser:
    """
    Parses natural-language petroleum/pipeline tender document clauses and converts them into
    structured requirement records with categories, numerical thresholds,
    period constraints, mandatory flags, and required evidence types.
    Integrates UnifiedRequirementExtractor (LLM + Regex + ML Classifier).
    """

    @staticmethod
    def parse_clauses_from_text(text: str) -> List[Dict[str, Any]]:
        if not text or not text.strip():
            return TenderRequirementParser.get_default_petroleum_pipeline_requirements()

        requirements = []
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        
        # Segment paragraphs / candidate requirement clauses
        paragraphs = []
        curr = []
        for l in lines:
            if re.match(r"^(?:Clause|[0-9]+[\.\)]|Section|[A-Z][\.\)]|CHECK\s*[0-9]+|REQ\s*[-–:]|Requirement\s*[0-9]*)\s+", l, re.IGNORECASE):
                if curr:
                    paragraphs.append(" ".join(curr))
                    curr = []
            curr.append(l)
        if curr:
            paragraphs.append(" ".join(curr))

        # If standard section regex didn't split into chunks, split on double newlines or sentence boundaries
        if len(paragraphs) <= 1:
            raw_blocks = [b.strip() for b in re.split(r"\n\s*\n|\.\s+(?=[A-Z0-9])", text) if len(b.strip()) > 25]
            if raw_blocks:
                paragraphs = raw_blocks

        # Import unified requirement extractor
        try:
            from app.ml.requirement_extractor import unified_requirement_extractor
        except ImportError:
            unified_requirement_extractor = None

        clause_idx = 1
        for p in paragraphs:
            # Skip noise / header / footer lines
            if len(p) < 15 or p.lower().startswith("generated:") or p.lower().startswith("page ") or p.lower().startswith("official stamp"):
                continue

            # Try unified 3-stage extractor first if available
            structured_req = None
            if unified_requirement_extractor:
                try:
                    ext = unified_requirement_extractor.extract(p)
                    cat = ext.get("category")
                    # If meaningful requirement category detected
                    if cat and cat not in ["TECHNICAL_SPECIFICATION", ""] or ext.get("threshold") or len(ext.get("entities", [])) > 0:
                        # Map locked class to backend requirement categories
                        cat_mapping = {
                            "GST_TAX_COMPLIANCE": "GST",
                            "MSME_UDYAM_ELIGIBILITY": "UDYAM",
                            "FINANCIAL_ELIGIBILITY": "TURNOVER",
                            "EXPERIENCE_ELIGIBILITY": "SIMILAR_PIPELINE_EXPERIENCE",
                            "OEM_AUTHORIZATION": "OEM",
                            "BLACKLISTING_DEBARMENT": "NON_BLACKLISTING",
                            "TECHNICAL_SPECIFICATION": "TECHNICAL_MANPOWER",
                            "INDUSTRY_STANDARD_COMPLIANCE": "SIMILAR_PIPELINE_EXPERIENCE",
                            "SAFETY_REGULATORY_COMPLIANCE": "HSE_SAFETY",
                            "MAKE_IN_INDIA_LOCAL_CONTENT": "LOCAL_CONTENT"
                        }
                        backend_cat = cat_mapping.get(cat, cat)
                        
                        # Determine evidence types based on category
                        ev_map = {
                            "GST": ["GST_REGISTRATION_CERTIFICATE", "LATEST_GSTR_3B_FILING"],
                            "PAN": ["PAN_CARD", "ITR_ACKNOWLEDGEMENT"],
                            "TURNOVER": ["AUDITED_FINANCIAL_STATEMENT", "CA_TURNOVER_CERTIFICATE"],
                            "SIMILAR_PIPELINE_EXPERIENCE": ["PIPELINE_COMPLETION_CERTIFICATE", "CLIENT_WORK_ORDER", "COMMISSIONING_REPORT"],
                            "OIL_GAS_EXPERIENCE": ["EXPERIENCE_CERTIFICATES", "CLIENT_COMPLETION_LETTERS"],
                            "TECHNICAL_MANPOWER": ["KEY_PERSONNEL_CVS", "DEGREE_CERTIFICATES", "EXPERIENCE_RECORDS"],
                            "HSE_SAFETY": ["ISO_45001_CERTIFICATE", "ISO_14001_CERTIFICATE", "SAFETY_POLICY_MANUAL"],
                            "OEM": ["MANUFACTURER_AUTHORIZATION_FORM_MAF", "OEM_WARRANTY_COMMITMENT"],
                            "LOCAL_CONTENT": ["LOCAL_CONTENT_SELF_DECLARATION", "COST_AUDITOR_CERTIFICATE"]
                        }

                        threshold_val = ext.get("threshold") or ext.get("minimum_value") or ext.get("value")
                        unit_val = ext.get("unit") or ("INR" if backend_cat == "TURNOVER" else ("KM" if backend_cat == "SIMILAR_PIPELINE_EXPERIENCE" else None))
                        period_val = f"LAST_{ext.get('time_period_years')}_YEARS" if ext.get("time_period_years") else ("CURRENT_ACTIVE" if backend_cat == "GST" else "ANNUAL")

                        structured_req = {
                            "category": backend_cat,
                            "clause_number": f"Cl-{clause_idx}",
                            "description": p,
                            "threshold": float(threshold_val) if threshold_val is not None else None,
                            "threshold_unit": unit_val,
                            "period": period_val,
                            "mandatory": True,
                            "evidence_required": ev_map.get(backend_cat, ["COMPLIANCE_CERTIFICATE"]),
                            "verification_method": "AI_HYBRID_EXTRACTOR",
                            "rule_version": "1.0",
                            "confidence": ext.get("confidence", 0.90)
                        }
                except Exception:
                    structured_req = None

            # Fallback to rule-based classification if unified extractor didn't match
            if not structured_req:
                structured_req = TenderRequirementParser.classify_and_structure_clause(p, clause_idx)

            if structured_req:
                requirements.append(structured_req)
                clause_idx += 1

        # ONLY fallback to default seed requirements if 0 requirements could be extracted from document text
        if len(requirements) == 0:
            requirements = TenderRequirementParser.get_default_petroleum_pipeline_requirements()

        return requirements

    @staticmethod
    def classify_and_structure_clause(clause_text: str, idx: int) -> Optional[Dict[str, Any]]:
        lower = clause_text.lower()

        # 1. GST Registration
        if "gst" in lower or "gstin" in lower:
            return {
                "category": "GST",
                "clause_number": f"Cl-{idx}",
                "description": clause_text,
                "threshold": None,
                "threshold_unit": None,
                "period": "CURRENT_ACTIVE",
                "mandatory": True,
                "evidence_required": ["GST_REGISTRATION_CERTIFICATE", "LATEST_GSTR_3B_FILING"],
                "verification_method": "PORTAL_AND_RULE",
                "rule_version": "1.0"
            }

        # 2. PAN / Income Tax
        elif "pan" in lower or "income tax" in lower or "itr" in lower:
            return {
                "category": "PAN",
                "clause_number": f"Cl-{idx}",
                "description": clause_text,
                "threshold": None,
                "threshold_unit": None,
                "period": "LAST_3_FINANCIAL_YEARS",
                "mandatory": True,
                "evidence_required": ["PAN_CARD", "ITR_ACKNOWLEDGEMENT"],
                "verification_method": "PORTAL_AND_RULE",
                "rule_version": "1.0"
            }

        # 3. Annual Financial Turnover
        elif "turnover" in lower or "annual financial turnover" in lower:
            threshold_match = re.search(r"(?:₹|rs\.?|inr)?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:cr|crore|crores|lakh|lakhs)", lower)
            threshold = 100000000.0  # Default 10 Cr (100,000,000 INR)
            unit = "INR"
            if threshold_match:
                num = float(threshold_match.group(1))
                if "lakh" in lower:
                    threshold = num * 100000.0
                else:
                    threshold = num * 10000000.0
                    
            period = "LAST_3_FINANCIAL_YEARS" if ("3" in lower or "three" in lower) else "ANNUAL"
            
            return {
                "category": "TURNOVER",
                "clause_number": f"Cl-{idx}",
                "description": clause_text,
                "threshold": threshold,
                "threshold_unit": unit,
                "period": period,
                "mandatory": True,
                "evidence_required": ["AUDITED_FINANCIAL_STATEMENT", "CA_TURNOVER_CERTIFICATE"],
                "verification_method": "RULE_AND_ARITHMETIC",
                "rule_version": "1.0"
            }

        # 5. Similar Pipeline Experience (Check this before generic Oil & Gas)
        elif ("pipeline" in lower and any(w in lower for w in ["length", "km", "diameter", "cross-country", "transmission", "similar", "executed"])) or "similar pipeline" in lower:
            km_match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(?:km|kms|kilometers)", lower)
            threshold_km = float(km_match.group(1)) if km_match else 100.0
            
            return {
                "category": "SIMILAR_PIPELINE_EXPERIENCE",
                "clause_number": f"Cl-{idx}",
                "description": clause_text,
                "threshold": threshold_km,
                "threshold_unit": "KM",
                "period": "LAST_7_YEARS",
                "mandatory": True,
                "evidence_required": ["PIPELINE_COMPLETION_CERTIFICATE", "CLIENT_WORK_ORDER", "COMMISSIONING_REPORT"],
                "verification_method": "RULE_AND_SEMANTIC",
                "rule_version": "1.0"
            }

        # 4. Oil & Gas Sector Experience
        elif any(w in lower for w in ["oil & gas", "oil and gas", "petroleum", "hydrocarbon", "refinery", "petrochemical"]):
            return {
                "category": "OIL_GAS_EXPERIENCE",
                "clause_number": f"Cl-{idx}",
                "description": clause_text,
                "threshold": None,
                "threshold_unit": None,
                "period": "LAST_5_TO_7_YEARS",
                "mandatory": True,
                "evidence_required": ["EXPERIENCE_CERTIFICATES", "CLIENT_COMPLETION_LETTERS"],
                "verification_method": "SEMANTIC_NLP_CLASSIFIER",
                "rule_version": "1.0"
            }

        # 6. Technical Manpower / Qualified Engineers
        elif any(w in lower for w in ["manpower", "personnel", "engineer", "engineers", "technical staff", "cvs"]):
            eng_match = re.search(r"(?:minimum|at least)?\s*([0-9]+)\s*(?:engineers?|personnel|staff|technical)", lower)
            count = float(eng_match.group(1)) if eng_match else 5.0
            return {
                "category": "TECHNICAL_MANPOWER",
                "clause_number": f"Cl-{idx}",
                "description": clause_text,
                "threshold": count,
                "threshold_unit": "PERSONNEL_COUNT",
                "period": "PROJECT_EXECUTION",
                "mandatory": True,
                "evidence_required": ["KEY_PERSONNEL_CVS", "DEGREE_CERTIFICATES", "EXPERIENCE_RECORDS"],
                "verification_method": "DETERMINISTIC_COUNT_AND_NLP",
                "rule_version": "1.0"
            }

        # 7 (Option A). HSE / Safety Management
        elif any(w in lower for w in ["hse", "safety", "iso 45001", "iso 14001", "health and safety", "environment management"]):
            return {
                "category": "HSE_SAFETY",
                "clause_number": f"Cl-{idx}",
                "description": clause_text,
                "threshold": None,
                "threshold_unit": None,
                "period": "VALID_CERTIFICATION",
                "mandatory": True,
                "evidence_required": ["ISO_45001_CERTIFICATE", "ISO_14001_CERTIFICATE", "SAFETY_POLICY_MANUAL"],
                "verification_method": "CERTIFICATION_VERIFIER",
                "rule_version": "1.0"
            }

        # 7 (Option B). OEM Authorization for Line Pipes / Equipment
        elif any(w in lower for w in ["oem", "manufacturer authorization", "maf", "line pipe manufacturer"]):
            return {
                "category": "OEM",
                "clause_number": f"Cl-{idx}",
                "description": clause_text,
                "threshold": None,
                "threshold_unit": None,
                "period": "TENDER_VALIDITY",
                "mandatory": True,
                "evidence_required": ["MANUFACTURER_AUTHORIZATION_FORM_MAF", "OEM_WARRANTY_COMMITMENT"],
                "verification_method": "RULE_AND_ENTITY_MATCH",
                "rule_version": "1.0"
            }

        # 7 (Option C). Make in India / Local Content
        elif any(w in lower for w in ["local content", "make in india", "mii", "indigenous content"]):
            threshold_match = re.search(r"([0-9]{1,3})\s*%", lower)
            threshold = float(threshold_match.group(1)) if threshold_match else 50.0
            return {
                "category": "LOCAL_CONTENT",
                "clause_number": f"Cl-{idx}",
                "description": clause_text,
                "threshold": threshold,
                "threshold_unit": "%",
                "period": "TENDER_SPECIFIC",
                "mandatory": True,
                "evidence_required": ["LOCAL_CONTENT_SELF_DECLARATION", "COST_AUDITOR_CERTIFICATE"],
                "verification_method": "RULE_AND_SEMANTIC",
                "rule_version": "1.0"
            }

        return None

    @staticmethod
    def get_default_petroleum_pipeline_requirements() -> List[Dict[str, Any]]:
        """
        Returns the standard 7 Core Petroleum & Natural Gas Pipeline Procurement compliance matrix.
        """
        return [
            {
                "category": "GST",
                "clause_number": "Cl-1.1",
                "description": "Bidder must possess valid and active GSTIN registration in the relevant State/UT and submit latest GSTR-3B filings.",
                "threshold": None,
                "threshold_unit": None,
                "period": "CURRENT_ACTIVE",
                "mandatory": True,
                "evidence_required": ["GST_REGISTRATION_CERTIFICATE", "LATEST_GSTR_3B_FILING"],
                "verification_method": "PORTAL_AND_RULE",
                "rule_version": "1.0"
            },
            {
                "category": "PAN",
                "clause_number": "Cl-1.2",
                "description": "Bidder entity must hold a valid Permanent Account Number (PAN) issued by Income Tax Department with matching legal corporate identity.",
                "threshold": None,
                "threshold_unit": None,
                "period": "PERMANENT",
                "mandatory": True,
                "evidence_required": ["PAN_CARD", "ITR_ACKNOWLEDGEMENTS"],
                "verification_method": "PORTAL_AND_RULE",
                "rule_version": "1.0"
            },
            {
                "category": "TURNOVER",
                "clause_number": "Cl-2.1",
                "description": "Average Annual Financial Turnover of the bidder during the last 3 preceding financial years (FY 2022-23, FY 2023-24, FY 2024-25) must be at least INR 10.00 Crore.",
                "threshold": 100000000.0,
                "threshold_unit": "INR",
                "period": "LAST_3_FINANCIAL_YEARS",
                "mandatory": True,
                "evidence_required": ["AUDITED_BALANCE_SHEETS", "CA_CERTIFIED_TURNOVER_STATEMENT"],
                "verification_method": "RULE_AND_ARITHMETIC",
                "rule_version": "1.0"
            },
            {
                "category": "OIL_GAS_EXPERIENCE",
                "clause_number": "Cl-3.1",
                "description": "Bidder must possess proven prior experience in executing EPC / construction works in the Petroleum, Natural Gas, Refinery, or Hydrocarbon pipeline sector.",
                "threshold": None,
                "threshold_unit": None,
                "period": "LAST_7_YEARS",
                "mandatory": True,
                "evidence_required": ["EXPERIENCE_CERTIFICATE", "CLIENT_COMPLETION_REPORT"],
                "verification_method": "SEMANTIC_NLP_CLASSIFIER",
                "rule_version": "1.0"
            },
            {
                "category": "SIMILAR_PIPELINE_EXPERIENCE",
                "clause_number": "Cl-3.2",
                "description": "Bidder must have successfully constructed and commissioned at least one cross-country high-pressure natural gas transmission pipeline of minimum 100 km length during the last 7 years.",
                "threshold": 100.0,
                "threshold_unit": "KM",
                "period": "LAST_7_YEARS",
                "mandatory": True,
                "evidence_required": ["PIPELINE_COMPLETION_CERTIFICATE", "CLIENT_TAKING_OVER_CERTIFICATE"],
                "verification_method": "RULE_AND_SEMANTIC",
                "rule_version": "1.0"
            },
            {
                "category": "TECHNICAL_MANPOWER",
                "clause_number": "Cl-4.1",
                "description": "Bidder must commit and deploy a minimum of 5 qualified pipeline engineers (B.Tech / B.E. Mechanical / Pipeline / NDT Level II) with at least 8 years of relevant site experience.",
                "threshold": 5.0,
                "threshold_unit": "PERSONNEL_COUNT",
                "period": "PROJECT_DEPLOYMENT",
                "mandatory": True,
                "evidence_required": ["KEY_PERSONNEL_CVS", "DEGREE_CERTIFICATES", "EXPERIENCE_AFFIDAVITS"],
                "verification_method": "DETERMINISTIC_COUNT_AND_NLP",
                "rule_version": "1.0"
            },
            {
                "category": "HSE_SAFETY",
                "clause_number": "Cl-5.1",
                "description": "Configurable Requirement: Bidder must maintain certified Occupational Health & Safety (ISO 45001) and Environmental Management (ISO 14001) systems with a zero-fatality site safety policy.",
                "threshold": None,
                "threshold_unit": None,
                "period": "VALID_CERTIFICATION",
                "mandatory": True,
                "evidence_required": ["ISO_45001_CERTIFICATE", "ISO_14001_CERTIFICATE", "CORPORATE_SAFETY_POLICY"],
                "verification_method": "CERTIFICATION_VERIFIER",
                "rule_version": "1.0"
            }
        ]
