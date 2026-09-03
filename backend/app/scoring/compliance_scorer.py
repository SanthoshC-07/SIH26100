from typing import Dict, Any, List
from app.core.config import settings

class ComplianceScorer:
    """
    Computes weighted compliance scores based on centralized scoring configuration.
    Produces both categorical breakdown and overall 0-100 score.
    """

    @staticmethod
    def calculate_score(
        compliance_checks: List[Dict[str, Any]],
        custom_weights: Dict[str, float] = None
    ) -> Dict[str, Any]:
        weights = custom_weights or settings.SCORING_WEIGHTS
        
        # Categorize checks for Petroleum & Natural Gas Procurement
        category_map = {
            "STATUTORY": ["GST", "PAN", "UDYAM", "EPFO", "ESIC", "BLACKLISTING", "MCA"],
            "FINANCIAL": ["TURNOVER", "NET_WORTH", "SOLVENCY"],
            "TENDER_SPECIFIC": [
                "OIL_GAS_EXPERIENCE", "SIMILAR_PIPELINE_EXPERIENCE",
                "TECHNICAL_MANPOWER", "OEM", "LOCAL_CONTENT", "HSE_SAFETY",
                "EXPERIENCE", "TENDER_SPECIFIC", "MANPOWER"
            ],
            "DOCUMENTATION": ["INTEGRITY_PACT", "DIGILOCKER", "DOCUMENTATION"],
            "OTHER_ELIGIBILITY": ["STARTUP_INDIA", "NSIC", "ISO", "QUALITY_CERTIFICATIONS", "EQUIPMENT_MACHINERY"]
        }

        # Initialize score buckets
        category_scores = {
            "STATUTORY": [],
            "FINANCIAL": [],
            "TENDER_SPECIFIC": [],
            "DOCUMENTATION": [],
            "OTHER_ELIGIBILITY": []
        }

        for check in compliance_checks:
            cat = (check.get("requirement_category") or "STATUTORY").upper()
            status = (check.get("status") or "REVIEW").upper()
            
            # Map status to numeric value
            if status == "PASS":
                val = 1.0
            elif status == "NOT_APPLICABLE":
                val = 1.0 # Neutralized full score
            elif status == "REVIEW":
                val = 0.50 # Partial credit pending officer review
            else: # FAIL
                val = 0.0

            assigned = False
            for bucket, cat_list in category_map.items():
                if cat in cat_list:
                    category_scores[bucket].append(val)
                    assigned = True
                    break
            if not assigned:
                category_scores["TENDER_SPECIFIC"].append(val)

        # Compute bucket averages (default 100% if no requirements in bucket)
        subscores = {}
        for bucket, vals in category_scores.items():
            if vals:
                avg = sum(vals) / len(vals)
            else:
                avg = 1.0
            subscores[bucket] = round(avg * 100.0, 1)

        # Weighted aggregate
        overall = 0.0
        for bucket, weight in weights.items():
            bucket_score = subscores.get(bucket, 100.0)
            overall += bucket_score * weight

        overall_score = round(max(0.0, min(100.0, overall)), 1)

        return {
            "overall_score": overall_score,
            "statutory_score": subscores["STATUTORY"],
            "financial_score": subscores["FINANCIAL"],
            "tender_specific_score": subscores["TENDER_SPECIFIC"],
            "documentation_score": subscores["DOCUMENTATION"],
            "other_score": subscores["OTHER_ELIGIBILITY"],
            "weights_applied": weights
        }
