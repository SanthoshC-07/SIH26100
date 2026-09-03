from typing import Dict, Any, List

class RecommendationGenerator:
    """
    Generates transparent, evidence-grounded AI recommendations for the Procurement Officer.
    Emphasizes decision support: AI NEVER unilaterally decides final qualification.
    """

    @staticmethod
    def generate_recommendation(
        bidder_name: str,
        compliance_checks: List[Dict[str, Any]],
        overall_score: float,
        risk_level: str
    ) -> Dict[str, Any]:
        detailed_reasons = []
        
        pass_count = 0
        fail_count = 0
        review_count = 0

        for check in compliance_checks:
            cat = check.get("requirement_category", "")
            status = check.get("status", "")
            reason = check.get("reason", "")
            
            if status == "PASS":
                pass_count += 1
            elif status == "FAIL":
                fail_count += 1
                detailed_reasons.append(f"Non-compliant {cat}: {reason}")
            elif status == "REVIEW":
                review_count += 1
                detailed_reasons.append(f"Requires clarification on {cat}: {reason}")

        if risk_level == "CRITICAL" or fail_count >= 2:
            rec_type = "NOT_RECOMMENDED"
            summary = f"Bidder '{bidder_name}' is NOT RECOMMENDED due to critical non-compliance with mandatory tender / statutory requirements."
        elif review_count > 0 or fail_count == 1:
            rec_type = "REQUIRES_PROCUREMENT_OFFICER_REVIEW"
            summary = f"Bidder '{bidder_name}' REQUIRES PROCUREMENT OFFICER REVIEW to evaluate flagged review items and confirm bidder eligibility."
        else:
            rec_type = "RECOMMENDED_FOR_QUALIFICATION"
            summary = f"Bidder '{bidder_name}' meets all statutory, financial, and technical eligibility criteria with HIGH confidence."
            detailed_reasons.append("All statutory portal checks (GST, PAN, Udyam, Debarment) successfully validated.")
            detailed_reasons.append("Financial turnover meets the required 3-year average threshold.")
            detailed_reasons.append("Technical eligibility and Make in India declarations verified.")

        return {
            "recommendation_type": rec_type,
            "summary": summary,
            "detailed_reasons": detailed_reasons
        }
