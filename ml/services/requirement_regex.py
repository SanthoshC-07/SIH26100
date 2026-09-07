"""
SIH26100 — Deterministic Regex Extraction Fallback Engine
---------------------------------------------------------
Deterministic regex extractor that parses domain-specific numerical and entity parameters:
- Currency: INR, Rs, ₹, Crore, Lakhs
- Distance: KM, Kilometers, Meters
- Diameter: Inch, Inches, NB, DN, mm
- Time Periods: Years, Months, FY, Financial Years
- Quantities: Counts, Personnel, Engineers
- Percentages: Local Content %, Weight %
- Standards: API, ASME, OISD, ISO, BIS

Authoritative Path:
    ml/services/requirement_regex.py
"""
import re
from typing import Dict, Any, List, Optional


class RegexRequirementExtractor:
    """
    Deterministic fallback engine for petroleum procurement requirements.
    Provides precise numerical parameter extraction when LLM extraction fails or is incomplete.
    """

    @classmethod
    def extract_deterministic_entities(cls, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            return {
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
                "extraction_method": "REGEX_FALLBACK"
            }

        res = {
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
            "confidence": 0.85,
            "extraction_method": "REGEX_FALLBACK"
        }
        lower = text.lower()

        # 1. Currency & Turnover (e.g. INR 25 Crore, ₹ 500 Lakh, Rs. 10 Cr)
        currency_match = re.search(
            r"(?:(inr|rs\.?|₹|inr\.?)\s*)?([0-9]+(?:\.[0-9]+)?)\s*(crore|cr|lakh|lac|thousand|k)s?",
            lower
        )
        if currency_match:
            curr_sym = currency_match.group(1)
            amt = float(currency_match.group(2))
            unit_raw = currency_match.group(3).upper()
            if "CR" in unit_raw:
                multiplier = 10000000.0
                unit = "CRORE"
            elif "LAC" in unit_raw or "LAKH" in unit_raw:
                multiplier = 100000.0
                unit = "LAKH"
            else:
                multiplier = 1000.0
                unit = "THOUSAND"

            res["value"] = amt * multiplier
            res["minimum_value"] = amt
            res["threshold"] = amt * multiplier
            res["unit"] = unit
            res["currency"] = "INR"
            res["entities"].append(f"Currency: {amt} {unit} (INR {res['value']:,.0f})")

        # Check for plain currency numbers like INR 50,00,000 or ₹ 2500000
        plain_curr = re.search(r"(?:inr|rs\.?|₹)\s*([0-9,]+(?:\.[0-9]+)?)", lower)
        if plain_curr and not currency_match:
            try:
                raw_amt_str = plain_curr.group(1).replace(",", "")
                plain_amt = float(raw_amt_str)
                res["value"] = plain_amt
                res["minimum_value"] = plain_amt
                res["threshold"] = plain_amt
                res["currency"] = "INR"
                res["unit"] = "INR"
                res["entities"].append(f"Currency: INR {plain_amt:,.0f}")
            except ValueError:
                pass

        # 2. Pipeline Length / Distance (e.g. 100 KM, 135.5 kms, 50 kilometers, 500 meters)
        km_match = re.search(
            r"([0-9]+(?:\.[0-9]+)?)\s*(?:km|kms|kilometer|kilometre|kilometers|kilometres)s?",
            lower
        )
        if km_match:
            km_val = float(km_match.group(1))
            res["length_km"] = km_val
            if not res["minimum_value"] and not res["threshold"]:
                res["minimum_value"] = km_val
                res["threshold"] = km_val
                res["unit"] = "KM"
            res["entities"].append(f"Length: {km_val} KM")

        meter_match = re.search(
            r"([0-9]+(?:\.[0-9]+)?)\s*(?:meter|metre|meters|metres|m)\b",
            lower
        )
        if meter_match and not km_match:
            m_val = float(meter_match.group(1))
            res["entities"].append(f"Length: {m_val} Meters")

        # 3. Pipe Diameter (e.g. 24 Inch, 24-inch NB, 30\", 600 mm)
        dia_match = re.search(
            r"([0-9]+(?:\.[0-9]+)?)\s*(?:inch|inches|\"|-inch|nb|dn)\b",
            lower
        )
        if dia_match:
            dia_val = float(dia_match.group(1))
            res["diameter_inch"] = dia_val
            res["entities"].append(f"Diameter: {dia_val} Inch")

        # 4. Experience in Years (e.g. 7 years experience, 8 years relevant experience, 7 years past experience)
        exp_match = re.search(
            r"([0-9]+)\s*(?:years?|yrs?)(?:\s*(?:prior|past|execution|sector|pipeline|relevant|work|industry|project|hands-on))?\s*experience",
            lower
        )
        if not exp_match:
            exp_match = re.search(
                r"experience\s*(?:of|for)?\s*(?:minimum|at least)?\s*([0-9]+)\s*(?:years?|yrs?)",
                lower
            )
        if not exp_match:
            exp_match = re.search(
                r"([0-9]+)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|track\s*record)",
                lower
            )
        if exp_match:
            exp_yrs = int(exp_match.group(1))
            res["experience_years"] = exp_yrs
            if res["minimum_value"] is None and res["length_km"] is None and res["value"] is None:
                res["minimum_value"] = exp_yrs
                res["unit"] = "YEARS"
            res["entities"].append(f"Experience: {exp_yrs} Years")

        # 5. Financial / Assessment Period in Years (e.g. last 3 financial years, 3 fiscal years, 3 years)
        period_match = re.search(
            r"(?:last|past|preceding|during)\s*([0-9]+)\s*(?:financial\s*years?|fiscal\s*years?|years?|fy)",
            lower
        )
        if period_match:
            res["time_period_years"] = int(period_match.group(1))
            res["entities"].append(f"Period: {period_match.group(1)} Years")

        # 5b. Months duration (e.g. 12 months, 6 months)
        months_match = re.search(r"([0-9]+)\s*(?:months?|mths?)\b", lower)
        if months_match:
            months_cnt = int(months_match.group(1))
            res["entities"].append(f"Duration: {months_cnt} Months")

        # 5c. Dates & Financial Year Years (e.g. FY 2023-24, FY 2024-25, 31-03-2025, 15-March-2025)
        fy_match = re.findall(r"(?:fy\s*)?20[0-9]{2}[-/][0-9]{2,4}", lower)
        for fy in fy_match:
            fy_clean = fy.strip().upper()
            res["entities"].append(f"Financial Year: {fy_clean}")
            if not res["date"]:
                res["date"] = fy_clean

        date_match = re.findall(r"\b([0-9]{1,2}[-/.][0-9]{1,2}[-/.][0-9]{2,4}|[0-9]{1,2}-(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*-[0-9]{2,4})\b", lower)
        for dt in date_match:
            dt_clean = dt.strip()
            res["entities"].append(f"Date: {dt_clean}")
            if not res["date"]:
                res["date"] = dt_clean

        # 6. Technical Manpower / Engineers count (e.g. 5 engineers, minimum 5 pipeline engineers)
        engineers_match = re.search(
            r"(?:minimum|at least)?\s*([0-9]+)\s*(?:qualified|certified|lead|pipeline|welding|safety|hse)?\s*(?:engineers?|personnel|inspectors?|supervisors?)",
            lower
        )
        if engineers_match:
            cnt = int(engineers_match.group(1))
            res["required_count"] = cnt
            res["count"] = cnt
            res["role"] = "Pipeline Engineer"
            res["entities"].append(f"Personnel: {cnt} Engineers")

        # 7. Local Content / Percentages (e.g. 50% local content, 40 percent)
        pct_match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(?:%|percent|percentage)", lower)
        if pct_match:
            pct_val = float(pct_match.group(1))
            res["percentage"] = pct_val
            res["entities"].append(f"Percentage: {pct_val}%")
            if ("local content" in lower or "make in india" in lower or "indigenous" in lower) and res.get("minimum_value") is None:
                res["value"] = pct_val
                res["minimum_value"] = pct_val
                res["threshold"] = pct_val
                res["unit"] = "%"

        # 8. Project Type & Sector Inferences
        if "natural gas" in lower:
            res["project_type"] = "Natural Gas Pipeline"
            res["sector"] = "Natural Gas"
        elif "crude" in lower or "oil" in lower or "petroleum" in lower or "hydrocarbon" in lower:
            res["project_type"] = "Oil & Gas Pipeline"
            res["sector"] = "Oil & Gas"

        # 9. Technical Standards
        for std in ["api 5l", "api 6d", "api 1104", "asme b31.8", "asme b31.4", "asme b16.34", "oisd-141", "oisd 141", "iso 45001", "iso 14001", "iso 9001"]:
            if std in lower:
                res["entities"].append(f"Standard: {std.upper()}")

        return res


regex_requirement_extractor = RegexRequirementExtractor()
