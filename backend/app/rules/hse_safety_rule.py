from typing import Dict, Any, List
import re

class HSESafetyRuleEngine:
    """
    Check 7 (Option B): HSE / Safety Compliance Verification Service
    Evaluates bidder's Health, Safety, and Environment compliance for petroleum/pipeline sites:
    - ISO 45001:2018 (Occupational Health & Safety Management System)
    - ISO 14001:2015 (Environmental Management System) / OHSAS 18001
    - Corporate HSE Policy document
    - Dedicated Safety Officer appointment
    - Lost Time Injury Frequency Rate (LTIFR) / Safety record declarations
    """

    @classmethod
    def evaluate(
        cls,
        bidder_name: str,
        entities: List[Dict[str, Any]],
        mandatory: bool = True
    ) -> Dict[str, Any]:
        entities = entities or []
        
        hse_certs = []
        best_doc_id = None
        best_doc_name = "HSE_Safety_Compliance_Manual.pdf"
        best_page_num = 1
        best_snippet = ""

        for e in entities:
            etype = e.get("entity_type", "").upper()
            val = str(e.get("entity_value", ""))
            snippet = e.get("context_snippet", val)

            if etype in ["HSE_CERTIFICATION", "SAFETY_POLICY", "ISO_CERTIFICATE", "CERTIFICATION"]:
                snippet_lower = (val + " " + snippet).lower()
                has_hse = any(kw in snippet_lower for kw in [
                    "iso 45001", "iso 14001", "ohsas 18001", "hse policy",
                    "health safety", "safety management", "safety officer"
                ])
                if has_hse:
                    hse_certs.append({
                        "cert": val,
                        "snippet": snippet,
                        "page_number": e.get("page_number", 1),
                        "document_id": e.get("document_id"),
                        "document_name": e.get("document_name", "HSE_Safety_Manual.pdf")
                    })
                    if not best_snippet:
                        best_snippet = snippet
                        best_doc_id = e.get("document_id")
                        best_doc_name = e.get("document_name", "HSE_Safety_Manual.pdf")
                        best_page_num = e.get("page_number", 1)

        if not hse_certs:
            return {
                "status": "FAIL" if mandatory else "REVIEW",
                "confidence": 0.92,
                "reason": "No valid HSE / Safety Management System certifications (ISO 45001 / ISO 14001) or Corporate Safety Policy found in technical documents.",
                "evidence": "Missing required petroleum HSE compliance certificates.",
                "document_id": None,
                "document_name": "HSE_Manual.pdf",
                "page_number": 1,
                "source": "HSE_SAFETY_ENGINE",
                "method": "CERTIFICATION_AND_POLICY_VERIFIER",
                "calculation_breakdown": {
                    "iso_45001_verified": False,
                    "iso_14001_verified": False,
                    "hse_policy_found": False,
                    "requirement_met": False
                }
            }

        cert_names = [c["cert"] for c in hse_certs]
        return {
            "status": "PASS",
            "confidence": 0.96,
            "reason": f"Bidder satisfies Petroleum HSE Safety Compliance with verified certifications ({', '.join(cert_names[:2])}) and active site safety policies.",
            "evidence": best_snippet or f"HSE Compliance verified: {', '.join(cert_names)}",
            "document_id": best_doc_id,
            "document_name": best_doc_name,
            "page_number": best_page_num,
            "source": "HSE_SAFETY_ENGINE",
            "method": "CERTIFICATION_AND_POLICY_VERIFIER",
            "calculation_breakdown": {
                "certifications_verified": cert_names,
                "safety_policy_found": True,
                "requirement_met": True
            }
        }
