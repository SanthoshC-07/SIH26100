from typing import Dict, Any, List, Optional
import re

class TurnoverRuleEngine:
    @staticmethod
    def normalize_to_crore(val_str: str, norm_val: Optional[Any] = None) -> float:
        """
        Normalizes currency string (₹, INR, Crore, Cr, Lakh, Million) to Crore (Cr).
        Preserves deterministic Python arithmetic.
        """
        if norm_val is not None:
            try:
                num = float(norm_val)
                if num >= 100000:  # Given in raw INR
                    return round(num / 10000000.0, 4)
                return round(num, 4)
            except (ValueError, TypeError):
                pass

        val_clean = str(val_str).replace(",", "").replace("₹", "").replace("INR", "").strip()

        # Check Lakh / Lac
        lakh_match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(?:Lakh|Lac|Lakhs)", val_clean, re.IGNORECASE)
        if lakh_match:
            return round(float(lakh_match.group(1)) / 100.0, 4)

        # Check Million
        million_match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(?:Million|Mn)", val_clean, re.IGNORECASE)
        if million_match:
            return round(float(million_match.group(1)) / 10.0, 4)

        # Check Crore / Cr
        cr_match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(?:Cr|Crore|Crores)", val_clean, re.IGNORECASE)
        if cr_match:
            return round(float(cr_match.group(1)), 4)

        # Standalone numeric value
        num_match = re.search(r"([0-9]+(?:\.[0-9]+)?)", val_clean)
        if num_match:
            v = float(num_match.group(1))
            if v >= 100000:
                return round(v / 10000000.0, 4)
            return round(v, 4)

        return 0.0

    @classmethod
    def evaluate(
        cls,
        required_threshold_inr: float,
        extracted_entities: List[Dict[str, Any]],
        mandatory: bool = True,
        required_years_count: int = 3
    ) -> Dict[str, Any]:
        """
        Deterministic arithmetic calculation of multi-year average turnover.
        Performs exact math: (FY1 + FY2 + FY3) / 3 >= Threshold.
        Checks for:
        - Conflicting values across documents for the same financial year -> REVIEW
        - Missing financial years (e.g. 2 of 3) -> INSUFFICIENT / REVIEW
        - Exact threshold comparison -> PASS / FAIL
        """
        threshold_cr = (required_threshold_inr or 100000000.0) / 10000000.0
        required_years = max(1, int(required_years_count or 3))

        turnover_items = [
            e for e in extracted_entities
            if e.get("entity_type", "").upper() in (
                "FINANCIAL_TURNOVER", "TURNOVER_ANNUAL", "TURNOVER",
                "ANNUAL_TURNOVER", "FINANCIAL_TURNOVER_ANNUAL"
            )
        ]

        if not turnover_items:
            return {
                "status": "FAIL" if mandatory else "INSUFFICIENT",
                "confidence": 0.98,
                "reason": "Audited Financial Statements or CA Turnover Certificate missing from bidder submission.",
                "evidence": "No financial turnover records found in submitted documents.",
                "document_id": None,
                "document_name": None,
                "page_number": 1,
                "source": "DETERMINISTIC_ARITHMETIC_ENGINE",
                "method": "EXACT_ARITHMETIC",
                "calculation_breakdown": {
                    "fy_values": {},
                    "average_cr": 0.0,
                    "required_cr": threshold_cr,
                    "difference_cr": -threshold_cr,
                    "passed": False
                }
            }

        fy_dict = {}
        fy_raw_dict = {}
        conflicts = []

        for item in turnover_items:
            val_text = item.get("entity_value", "")
            snippet = item.get("context_snippet", "")
            combined_text = f"{val_text} {snippet}"

            # Match FY pattern e.g. "FY 2023-24" or "FY2023-24"
            fy_match = re.search(r"(202[0-9](?:-|\s*to\s*|/)(?:2[0-9]|[0-9]{2}))", combined_text)
            fy_key = fy_match.group(1).replace(" ", "") if fy_match else None

            val_cr = cls.normalize_to_crore(val_text, item.get("normalized_value"))
            if val_cr <= 0:
                continue

            if fy_key:
                if fy_key in fy_dict:
                    existing_val = fy_dict[fy_key]
                    if abs(existing_val - val_cr) > 0.1:
                        conflicts.append(f"{fy_key}: ₹{existing_val:g} Cr vs ₹{val_cr:g} Cr")
                else:
                    fy_dict[fy_key] = val_cr
                    fy_raw_dict[fy_key] = val_text
            else:
                default_key = f"FY-{len(fy_dict) + 1}"
                fy_dict[default_key] = val_cr
                fy_raw_dict[default_key] = val_text

        # 1. Check for conflicting values across documents for same FY
        if conflicts:
            return {
                "status": "REVIEW",
                "confidence": 0.85,
                "reason": f"Conflicting turnover values detected across submitted financial documents: {'; '.join(conflicts)}.",
                "evidence": f"Turnover discrepancies: {'; '.join(conflicts)}",
                "document_id": turnover_items[0].get("document_id") if turnover_items else None,
                "document_name": turnover_items[0].get("document_name") if turnover_items else "Audited_Financial_Statement.pdf",
                "page_number": turnover_items[0].get("page_number", 1) if turnover_items else 1,
                "source": "CROSS_DOCUMENT_CONSISTENCY",
                "method": "DOCUMENT_CONSISTENCY_CHECK",
                "calculation_breakdown": {
                    "fy_values": fy_dict,
                    "conflicts": conflicts,
                    "passed": False
                }
            }

        # 2. Check for missing years if required years specified
        if len(fy_dict) < required_years:
            vals_str = " + ".join([f"{v:g}" for v in fy_dict.values()]) if fy_dict else "0"
            submitted_avg = round(sum(fy_dict.values()) / max(1, len(fy_dict)), 2)
            return {
                "status": "REVIEW" if mandatory else "INSUFFICIENT",
                "confidence": 0.90,
                "reason": f"Missing financial year data: only {len(fy_dict)} of required {required_years} financial years submitted ({', '.join(fy_dict.keys())}).",
                "evidence": f"Submitted {len(fy_dict)} years ({', '.join(fy_dict.keys())}): ({vals_str}) / {len(fy_dict)} = ₹{submitted_avg:g} Cr against mandatory {required_years}-year requirement.",
                "document_id": turnover_items[0].get("document_id") if turnover_items else None,
                "document_name": turnover_items[0].get("document_name") if turnover_items else "Audited_Financial_Statement.pdf",
                "page_number": turnover_items[0].get("page_number", 1) if turnover_items else 1,
                "source": "DETERMINISTIC_ARITHMETIC_ENGINE",
                "method": "COMPLETENESS_CHECK",
                "calculation_breakdown": {
                    "fy_values": fy_dict,
                    "submitted_years": len(fy_dict),
                    "required_years": required_years,
                    "passed": False
                }
            }

        # 3. Exact Python arithmetic average
        fy_values_list = list(fy_dict.values())
        total_sum = sum(fy_values_list)
        count = len(fy_values_list)
        avg_turnover_cr = round(total_sum / count, 2)
        passed = avg_turnover_cr >= threshold_cr

        vals_str = " + ".join([f"{v:g}" for v in fy_values_list])
        formula_display = f"({vals_str}) / {count} = {avg_turnover_cr:g} Cr"
        breakdown_str = " | ".join([f"{fy}: ₹{val:g} Cr" for fy, val in fy_dict.items()])

        first_doc = turnover_items[0] if turnover_items else None

        calc_payload = {
            "fy_values": fy_dict,
            "fy_raw_values": fy_raw_dict,
            "formula_display": formula_display,
            "average_cr": avg_turnover_cr,
            "required_cr": threshold_cr,
            "difference_cr": round(avg_turnover_cr - threshold_cr, 2),
            "passed": passed
        }

        if passed:
            return {
                "status": "PASS",
                "confidence": 0.99,
                "reason": f"Average annual turnover satisfies the tender threshold: {formula_display} (>= ₹{threshold_cr:g} Cr).",
                "evidence": f"Turnover Breakdown: {breakdown_str} ==> Arithmetic Average: {formula_display} >= Required: ₹{threshold_cr:g} Cr",
                "document_id": first_doc.get("document_id") if first_doc else None,
                "document_name": first_doc.get("document_name") if first_doc else "Audited_Financial_Statement.pdf",
                "page_number": first_doc.get("page_number", 1) if first_doc else 1,
                "source": "DETERMINISTIC_ARITHMETIC_ENGINE",
                "method": "EXACT_ARITHMETIC",
                "calculation_breakdown": calc_payload
            }
        else:
            return {
                "status": "FAIL",
                "confidence": 0.99,
                "reason": f"Calculated {count}-year average turnover of ₹{avg_turnover_cr:g} Cr is below mandatory threshold of ₹{threshold_cr:g} Cr (Shortfall: ₹{abs(avg_turnover_cr - threshold_cr):g} Cr).",
                "evidence": f"Turnover Breakdown: {breakdown_str} ==> Arithmetic Average: {formula_display} < Required: ₹{threshold_cr:g} Cr",
                "document_id": first_doc.get("document_id") if first_doc else None,
                "document_name": first_doc.get("document_name") if first_doc else "Audited_Financial_Statement.pdf",
                "page_number": first_doc.get("page_number", 1) if first_doc else 1,
                "source": "DETERMINISTIC_ARITHMETIC_ENGINE",
                "method": "EXACT_ARITHMETIC",
                "calculation_breakdown": calc_payload
            }
