from typing import Dict, Any, List
import re

class TurnoverRuleEngine:
    @staticmethod
    def evaluate(
        required_threshold_inr: float,
        extracted_entities: List[Dict[str, Any]],
        mandatory: bool = True
    ) -> Dict[str, Any]:
        """
        Deterministic arithmetic calculation of 3-year average turnover.
        Ensures exact math calculations without LLM hallucinations.
        """
        threshold_cr = (required_threshold_inr or 100000000.0) / 10000000.0
        
        # Collect extracted turnover entities
        turnover_items = [e for e in extracted_entities if e.get("entity_type") == "FINANCIAL_TURNOVER"]
        
        fy_dict = {}
        for item in turnover_items:
            # Parse text "FY 2023-24: ₹12.00 Cr"
            val_text = item.get("entity_value", "")
            match = re.search(r"(202[0-9](?:-|\s*to\s*|/)(?:2[0-9]|[0-9]{2}))\D{0,20}?₹?([0-9]+(?:\.[0-9]+)?)\s*Cr", val_text)
            if match:
                fy = match.group(1).replace(" ", "")
                val = float(match.group(2))
                fy_dict[fy] = val
        
        # Fallback if specific formatting
        if not fy_dict and turnover_items:
            for idx, item in enumerate(turnover_items[:3]):
                try:
                    val_inr = float(item.get("normalized_value", 0))
                    fy_dict[f"FY-{idx+1}"] = val_inr / 10000000.0
                except ValueError:
                    pass

        if not fy_dict:
            return {
                "status": "FAIL" if mandatory else "REVIEW",
                "confidence": 0.95,
                "reason": "Audited Financial Statements or CA Turnover Certificate missing from bidder submission.",
                "evidence": "No financial turnover records found for the required 3 financial years.",
                "document_id": None,
                "document_name": None,
                "page_number": 1,
                "source": "RULE_ENGINE",
                "method": "ARITHMETIC_VERIFICATION",
                "calculation_breakdown": {
                    "fy_values": {},
                    "average_cr": 0.0,
                    "required_cr": threshold_cr,
                    "difference_cr": -threshold_cr,
                    "passed": False
                }
            }

        # Calculate average
        fy_values_list = list(fy_dict.values())
        avg_turnover_cr = sum(fy_values_list) / max(1, len(fy_values_list))
        avg_turnover_cr = round(avg_turnover_cr, 2)
        passed = avg_turnover_cr >= threshold_cr

        # Build formatted calculation display
        breakdown_str = " | ".join([f"{fy}: ₹{val:.2f} Cr" for fy, val in fy_dict.items()])
        
        first_doc = turnover_items[0] if turnover_items else None
        
        calc_payload = {
            "fy_values": fy_dict,
            "average_cr": avg_turnover_cr,
            "required_cr": threshold_cr,
            "difference_cr": round(avg_turnover_cr - threshold_cr, 2),
            "passed": passed
        }

        if passed:
            return {
                "status": "PASS",
                "confidence": 0.99,
                "reason": f"Calculated 3-year average turnover of ₹{avg_turnover_cr:.2f} Cr meets/exceeds the required threshold of ₹{threshold_cr:.2f} Cr.",
                "evidence": f"Turnover Breakdown: {breakdown_str} ==> Average: ₹{avg_turnover_cr:.2f} Cr >= Required: ₹{threshold_cr:.2f} Cr",
                "document_id": first_doc.get("document_id") if first_doc else None,
                "document_name": first_doc.get("document_name") if first_doc else "Audited_Financial_Statement.pdf",
                "page_number": first_doc.get("page_number", 1) if first_doc else 1,
                "source": "RULE_ENGINE",
                "method": "ARITHMETIC_VERIFICATION",
                "calculation_breakdown": calc_payload
            }
        else:
            return {
                "status": "FAIL",
                "confidence": 0.99,
                "reason": f"Calculated 3-year average turnover of ₹{avg_turnover_cr:.2f} Cr is below the mandatory threshold of ₹{threshold_cr:.2f} Cr (Shortfall: ₹{abs(avg_turnover_cr - threshold_cr):.2f} Cr).",
                "evidence": f"Turnover Breakdown: {breakdown_str} ==> Average: ₹{avg_turnover_cr:.2f} Cr < Required: ₹{threshold_cr:.2f} Cr",
                "document_id": first_doc.get("document_id") if first_doc else None,
                "document_name": first_doc.get("document_name") if first_doc else "Audited_Financial_Statement.pdf",
                "page_number": first_doc.get("page_number", 1) if first_doc else 1,
                "source": "RULE_ENGINE",
                "method": "ARITHMETIC_VERIFICATION",
                "calculation_breakdown": calc_payload
            }
