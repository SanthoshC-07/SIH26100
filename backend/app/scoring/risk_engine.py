from typing import Dict, Any, List

class RiskEngine:
    """
    Evaluates multi-factor bid risk:
    - LOW: Strong compliance, zero critical issues, high confidence.
    - MEDIUM: Minor ambiguities or single non-mandatory item requiring review.
    - HIGH: Mandatory requirement failure or significant inconsistencies.
    - CRITICAL: Blacklist / Debarment hit or severe multiple failures.
    """

    @staticmethod
    def assess_risk(
        compliance_checks: List[Dict[str, Any]],
        overall_score: float
    ) -> Dict[str, Any]:
        risk_factors = []
        has_blacklist = False
        mandatory_failures = 0
        review_count = 0
        low_confidence_count = 0

        for check in compliance_checks:
            cat = (check.get("requirement_category") or "").upper()
            status = (check.get("status") or "").upper()
            mandatory = check.get("requirement_mandatory", True)
            confidence = check.get("confidence", 1.0)
            reason = check.get("reason", "")

            if cat == "BLACKLISTING" and status == "FAIL":
                has_blacklist = True
                risk_factors.append("CRITICAL: Vendor identified in Debarred/Blacklisted registry.")

            if status == "FAIL" and mandatory:
                mandatory_failures += 1
                risk_factors.append(f"Mandatory {cat} failure: {reason}")

            if status == "REVIEW":
                review_count += 1
                risk_factors.append(f"{cat} review required: {reason}")

            if confidence < 0.70:
                low_confidence_count += 1

        # Classify risk level
        if has_blacklist or mandatory_failures >= 2:
            risk_level = "CRITICAL"
            risk_score = 90.0
        elif mandatory_failures == 1 or (review_count >= 2 and overall_score < 75):
            risk_level = "HIGH"
            risk_score = 70.0
        elif review_count > 0 or overall_score < 85:
            risk_level = "MEDIUM"
            risk_score = 40.0
        else:
            risk_level = "LOW"
            risk_score = 10.0

        if not risk_factors:
            risk_factors.append("No critical risk factors identified. Bid exhibits robust statutory and tender compliance.")

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "primary_risk_factors": risk_factors
        }
