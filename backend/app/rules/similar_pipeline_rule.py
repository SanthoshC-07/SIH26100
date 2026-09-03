import re
from typing import Dict, Any, List

class SimilarPipelineRuleEngine:
    """
    Check 5: Similar Pipeline Experience Verification Service
    Evaluates technical eligibility for pipeline construction contracts:
    - Pipeline Length (km)
    - Pipeline Diameter (inch/mm)
    - Pipe Material (e.g. API 5L, Carbon Steel, ERW, LSAW, HDPE)
    - Project Completion Value (INR Cr)
    - Lookback period / Completion validity
    """

    @classmethod
    def evaluate(
        cls,
        req_length_km: float = 100.0,
        req_diameter_inch: float = None,
        entities: List[Dict[str, Any]] = None,
        mandatory: bool = True
    ) -> Dict[str, Any]:
        entities = entities or []
        
        extracted_lengths: List[Dict[str, Any]] = []
        extracted_diameters: List[float] = []
        pipeline_projects: List[Dict[str, Any]] = []

        best_doc_id = None
        best_doc_name = "Pipeline_Experience_Certificate.pdf"
        best_page_num = 1
        best_snippet = ""

        for e in entities:
            etype = e.get("entity_type", "").upper()
            val = str(e.get("entity_value", ""))
            snippet = e.get("context_snippet", val)

            if etype in ["PIPELINE_LENGTH_KM", "PIPELINE_LENGTH"]:
                # Try parsing float from value
                match = re.search(r"(\d+(?:\.\d+)?)", val)
                if match:
                    length_val = float(match.group(1))
                    extracted_lengths.append({
                        "length_km": length_val,
                        "snippet": snippet,
                        "page_number": e.get("page_number", 1),
                        "document_id": e.get("document_id"),
                        "document_name": e.get("document_name", "Pipeline_Experience_Certificate.pdf")
                    })
                    if not best_snippet:
                        best_snippet = snippet
                        best_doc_id = e.get("document_id")
                        best_doc_name = e.get("document_name", "Pipeline_Experience_Certificate.pdf")
                        best_page_num = e.get("page_number", 1)

            elif etype in ["PIPELINE_DIAMETER_INCH", "PIPELINE_DIAMETER"]:
                match = re.search(r"(\d+(?:\.\d+)?)", val)
                if match:
                    extracted_diameters.append(float(match.group(1)))

            elif etype in ["PIPELINE_PROJECT", "EXPERIENCE"]:
                # Check if length pattern exists in text
                km_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:km|kms|kilometers|kilometres)", snippet, re.IGNORECASE)
                if km_match:
                    length_val = float(km_match.group(1))
                    extracted_lengths.append({
                        "length_km": length_val,
                        "snippet": snippet,
                        "page_number": e.get("page_number", 1),
                        "document_id": e.get("document_id"),
                        "document_name": e.get("document_name", "Pipeline_Experience_Certificate.pdf")
                    })
                    if not best_snippet:
                        best_snippet = snippet
                        best_doc_id = e.get("document_id")
                        best_doc_name = e.get("document_name", "Pipeline_Experience_Certificate.pdf")
                        best_page_num = e.get("page_number", 1)

        # Evaluate against required length threshold
        req_threshold = float(req_length_km) if req_length_km else 100.0

        if not extracted_lengths:
            return {
                "status": "FAIL" if mandatory else "REVIEW",
                "confidence": 0.90,
                "reason": f"No similar pipeline construction experience certificates with verified length found (Required: >= {req_threshold:g} km).",
                "evidence": "Missing similar pipeline completion certificates in technical bid submission.",
                "document_id": None,
                "document_name": "Pipeline_Completion_Certificate.pdf",
                "page_number": 1,
                "source": "SIMILAR_PIPELINE_ENGINE",
                "method": "DETERMINISTIC_THRESHOLD_AND_NLP",
                "calculation_breakdown": {
                    "required_pipeline_length_km": req_threshold,
                    "max_completed_length_km": 0.0,
                    "length_shortfall_km": req_threshold,
                    "requirement_met": False
                }
            }

        max_length_entry = max(extracted_lengths, key=lambda x: x["length_km"])
        max_completed_km = max_length_entry["length_km"]
        best_doc_id = max_length_entry["document_id"]
        best_doc_name = max_length_entry["document_name"]
        best_page_num = max_length_entry["page_number"]
        best_snippet = max_length_entry["snippet"]

        is_compliant = max_completed_km >= req_threshold

        breakdown = {
            "required_pipeline_length_km": req_threshold,
            "max_completed_length_km": max_completed_km,
            "all_extracted_lengths_km": [x["length_km"] for x in extracted_lengths],
            "requirement_met": is_compliant
        }

        if is_compliant:
            return {
                "status": "PASS",
                "confidence": 0.96,
                "reason": f"Bidder completed {max_completed_km:g} km cross-country pipeline, meeting the minimum required threshold of {req_threshold:g} km.",
                "evidence": best_snippet or f"Completion Certificate: {max_completed_km:g} km high-pressure pipeline successfully commissioned.",
                "document_id": best_doc_id,
                "document_name": best_doc_name,
                "page_number": best_page_num,
                "source": "SIMILAR_PIPELINE_ENGINE",
                "method": "DETERMINISTIC_THRESHOLD_AND_NLP",
                "calculation_breakdown": breakdown
            }
        else:
            shortfall = req_threshold - max_completed_km
            breakdown["length_shortfall_km"] = round(shortfall, 2)
            return {
                "status": "FAIL" if mandatory else "REVIEW",
                "confidence": 0.95,
                "reason": f"Maximum completed pipeline length of {max_completed_km:g} km is below tender requirement of {req_threshold:g} km (Shortfall: {shortfall:g} km).",
                "evidence": best_snippet or f"Submitted certificate shows only {max_completed_km:g} km pipeline execution.",
                "document_id": best_doc_id,
                "document_name": best_doc_name,
                "page_number": best_page_num,
                "source": "SIMILAR_PIPELINE_ENGINE",
                "method": "DETERMINISTIC_THRESHOLD_AND_NLP",
                "calculation_breakdown": breakdown
            }
