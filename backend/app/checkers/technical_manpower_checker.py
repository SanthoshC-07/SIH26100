from typing import Dict, Any, List
from app.checkers.base_checker import BaseChecker
from app.rules.technical_manpower_rule import TechnicalManpowerRuleEngine

class TechnicalManpowerChecker(BaseChecker):
    """
    Check 6: Technical Manpower & Key Engineering Staff Verification Service
    Evaluates engineer count and individual experience years (e.g. >= 5 engineers with >= 8 years).
    """
    def get_checker_name(self) -> str:
        return "TechnicalManpowerChecker"

    def verify(
        self,
        requirement: Dict[str, Any],
        bidder: Dict[str, Any],
        evidence_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        req_count = int(requirement.get("required_manpower_count") or requirement.get("threshold") or 5)
        req_exp = float(requirement.get("required_years") or 8.0)
        mandatory = requirement.get("mandatory", True)
        entities = evidence_context.get("entities", [])
        
        # 1. Check structured BidderPersonnel database records
        personnel = bidder.get("personnel", [])
        if personnel:
            qualifying = [
                p for p in personnel
                if (p.get("years_of_experience", 0.0) >= req_exp or p.get("pipeline_experience_years", 0.0) >= req_exp)
            ]
            qual_count = len(qualifying)
            is_compliant = qual_count >= req_count

            breakdown = {
                "required_qualifying_engineers": req_count,
                "required_min_experience_years": req_exp,
                "total_submitted_personnel": len(personnel),
                "qualifying_personnel_count": qual_count,
                "qualifying_staff": [
                    {"name": p.get("name"), "designation": p.get("designation"), "experience_years": p.get("years_of_experience")}
                    for p in qualifying
                ],
                "requirement_met": is_compliant
            }

            if is_compliant:
                names_summary = ", ".join([p.get("name") for p in qualifying[:4]])
                return {
                    "status": "PASS",
                    "confidence": 0.98,
                    "evidence": f"Structured Manpower Records: {qual_count} senior engineers deployed ({names_summary}) meeting >= {req_exp:g} years experience.",
                    "reason": f"Bidder deployed {qual_count} qualified engineers, exceeding the required threshold of {req_count}.",
                    "document_id": qualifying[0].get("document_id") if qualifying else None,
                    "document_name": "Key_Personnel_CVs.pdf",
                    "page_number": 1,
                    "source": "STRUCTURED_BIDDER_PERSONNEL_DATABASE",
                    "method": "DETERMINISTIC_COUNTING",
                    "verification_details": breakdown
                }
            else:
                shortfall = req_count - qual_count
                breakdown["shortfall_count"] = shortfall
                return {
                    "status": "FAIL" if mandatory else "REVIEW",
                    "confidence": 0.95,
                    "evidence": f"Only {qual_count} of {req_count} deployed engineers meet the minimum {req_exp:g} years pipeline experience criteria.",
                    "reason": f"Technical staff shortfall: {qual_count} qualifying engineers found vs {req_count} required (Shortfall: {shortfall}).",
                    "document_id": personnel[0].get("document_id") if personnel else None,
                    "document_name": "Key_Personnel_CVs.pdf",
                    "page_number": 1,
                    "source": "STRUCTURED_BIDDER_PERSONNEL_DATABASE",
                    "method": "DETERMINISTIC_COUNTING",
                    "verification_details": breakdown
                }

        # 2. Fallback to entity extraction & document text
        res = TechnicalManpowerRuleEngine.evaluate(req_count, req_exp, entities, mandatory)
        return {
            "status": res.get("status", "REVIEW"),
            "confidence": res.get("confidence", 0.92),
            "evidence": res.get("evidence", ""),
            "reason": res.get("reason", ""),
            "document_id": res.get("document_id"),
            "document_name": res.get("document_name"),
            "page_number": res.get("page_number", 1),
            "source": res.get("source", "TECHNICAL_MANPOWER_ENGINE"),
            "method": res.get("method", "DETERMINISTIC_COUNTING_AND_NLP"),
            "verification_details": res.get("calculation_breakdown", {})
        }
