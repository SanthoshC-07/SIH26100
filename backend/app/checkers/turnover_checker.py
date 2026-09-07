from typing import Dict, Any, List
from app.checkers.base_checker import BaseChecker
from app.rules.turnover_rule import TurnoverRuleEngine
from app.documents.requirement_extractors import FinancialEligibilityExtractor

class TurnoverChecker(BaseChecker):
    """
    Check 3: Financial Turnover Deterministic Arithmetic
    Calculates:
    - Multi-year average annual turnover
    - Explicit mathematical formula display
    - Threshold comparison (e.g. 27 >= 25 Cr -> PASS)
    """
    def get_checker_name(self) -> str:
        return "TurnoverChecker"

    def verify(
        self,
        requirement: Dict[str, Any],
        evidence: Dict[str, Any],
        bidder: Dict[str, Any]
    ) -> Dict[str, Any]:
        threshold = requirement.get("threshold") or 250000000.0
        required_years = int(requirement.get("time_period_years") or requirement.get("required_years") or 3)
        entities = evidence.get("entities", [])
        mandatory = requirement.get("mandatory", True)
        req_cr = (threshold or 0) / 10000000.0

        res = TurnoverRuleEngine.evaluate(threshold, entities, mandatory, required_years_count=required_years)
        
        calc = res.get("calculation_breakdown", {})
        fy_vals = calc.get("fy_values", {})
        avg_cr = calc.get("average_cr", 0.0)
        passed = calc.get("passed", False)
        
        vals_str = " + ".join([f"{v:g}" for v in fy_vals.values()]) if fy_vals else "0"
        count = len(fy_vals) if fy_vals else 1
        formula_str = f"({vals_str}) / {count} = {avg_cr:g} Crore" if fy_vals else f"{avg_cr:g} Crore"
        
        doc_name = res.get("document_name") or "Audited_Financial_Statement.pdf"
        page_num = res.get("page_number", 1)
        status = res.get("status", "REVIEW")
        confidence = res.get("confidence", 0.99)
        reason = res.get("reason", "")
        evidence_text = res.get("evidence", "")

        # Extract structured requirement-specific fields
        raw_doc_text = evidence.get("source_text") or evidence_text or ""
        fin_ext = FinancialEligibilityExtractor.extract(
            text=raw_doc_text,
            pages=[{"page_number": page_num, "text": raw_doc_text}],
            document_name=doc_name,
            minimum_required_cr=req_cr
        )

        evidence_list = [
            {
                "document_name": doc_name,
                "document_id": res.get("document_id"),
                "page_number": page_num,
                "text": fin_ext.get("summary") or evidence_text,
                "extraction_method": "PDF_TEXT"
            }
        ] if evidence_text or fin_ext.get("summary") else []

        is_pass = status == "PASS"
        rule_results = [
            {
                "rule": "Average Annual Turnover Arithmetic",
                "condition": f"{formula_str} (>= {req_cr:g} Cr)",
                "passed": is_pass
            }
        ]

        extracted_req = {
            "category": "FINANCIAL_ELIGIBILITY",
            "minimum_value": req_cr,
            "unit": "CRORE",
            "threshold": threshold,
            "time_period_years": count,
            "mandatory": mandatory
        }

        cross_consistency = {
            "audited_figures_found": bool(fy_vals or fin_ext["data"].get("financial_years")),
            "years_evaluated": list(fy_vals.keys()) if fy_vals else fin_ext["data"].get("financial_years", []),
            "discrepancies": [] if is_pass else [reason]
        }

        return self.format_compliance_result(
            requirement_id=requirement.get("id") or "REQ-TURNOVER",
            status=status,
            confidence=confidence,
            requirement_text=requirement.get("description") or f"Minimum average annual turnover of INR {req_cr:g} Crore.",
            extracted_requirement=extracted_req,
            evidence_list=evidence_list,
            rule_results=rule_results,
            semantic_score=1.0,
            cross_document_consistency=cross_consistency,
            explanation=reason,
            risk="LOW" if is_pass else "HIGH",
            extra_metadata={
                "source": res.get("source", "RULE_ENGINE"),
                "method": res.get("method", "DETERMINISTIC_PYTHON_ARITHMETIC"),
                "verification_details": {
                    **calc,
                    "data": fin_ext.get("data", {}),
                    "fields": fin_ext.get("fields", []),
                    "summary": fin_ext.get("summary", ""),
                    "formula_display": formula_str,
                    "comparison": f"₹{avg_cr:g} Cr >= ₹{req_cr:g} Cr" if passed else f"₹{avg_cr:g} Cr < ₹{req_cr:g} Cr"
                }
            }
        )
