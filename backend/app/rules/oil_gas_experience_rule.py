import re
from typing import Dict, Any, List
from app.ml.semantic_matcher import SemanticComplianceMatcher

class OilGasExperienceRuleEngine:
    """
    Check 4: Oil & Gas Experience Verification Service
    Evaluates whether bidder has proven execution experience in the Oil & Gas / Petroleum energy sector.
    Uses semantic understanding and sector classification.
    """
    
    OIL_GAS_KEYWORDS = [
        "oil & gas", "oil and gas", "petroleum", "natural gas", "refinery",
        "petrochemical", "gas transmission", "cross-country pipeline",
        "hydrocarbon", "lng terminal", "lpg bottling", "gail", "iocl",
        "ongc", "bpcl", "hpcl", "city gas distribution", "cgd network"
    ]

    @classmethod
    def evaluate(
        cls,
        bidder_name: str,
        entities: List[Dict[str, Any]],
        mandatory: bool = True,
        doc_chunks: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        matched_projects = []
        highest_confidence = 0.0
        best_evidence = ""
        best_doc_id = None
        best_doc_name = "Experience_Certificate.pdf"
        best_page_num = 1

        # 1. Check extracted entities for OIL_GAS_PROJECT or EXPERIENCE
        for e in entities:
            etype = e.get("entity_type", "").upper()
            val = e.get("entity_value", "")
            snippet = e.get("context_snippet", val)
            
            if etype in ["OIL_GAS_PROJECT", "PROJECT_EXPERIENCE", "EXPERIENCE"]:
                val_lower = (val + " " + snippet).lower()
                matches = [kw for kw in cls.OIL_GAS_KEYWORDS if kw in val_lower]
                if matches:
                    matched_projects.append({
                        "project": val,
                        "snippet": snippet,
                        "keywords": matches,
                        "page_number": e.get("page_number", 1),
                        "document_id": e.get("document_id"),
                        "document_name": e.get("document_name", "Experience_Certificate.pdf")
                    })
                    highest_confidence = max(highest_confidence, e.get("confidence", 0.92))
                    if not best_evidence:
                        best_evidence = snippet
                        best_doc_id = e.get("document_id")
                        best_doc_name = e.get("document_name", "Experience_Certificate.pdf")
                        best_page_num = e.get("page_number", 1)

        # 2. Semantic Fallback using doc_chunks if entity extraction was sparse
        if not matched_projects and doc_chunks:
            semantic_res = SemanticComplianceMatcher.match_evidence(
                "Execution experience in oil and gas, petroleum, refinery, or natural gas transmission projects.",
                doc_chunks
            )
            if semantic_res.get("confidence", 0) > 0.65:
                matched_projects.append({
                    "project": semantic_res.get("evidence_snippet", ""),
                    "snippet": semantic_res.get("evidence_snippet", ""),
                    "keywords": ["semantic_match"],
                    "page_number": semantic_res.get("page_number", 1),
                    "document_id": semantic_res.get("document_id"),
                    "document_name": semantic_res.get("document_name", "Experience_Certificate.pdf")
                })
                highest_confidence = semantic_res.get("confidence", 0.85)
                best_evidence = semantic_res.get("evidence_snippet", "")
                best_doc_id = semantic_res.get("document_id")
                best_doc_name = semantic_res.get("document_name", "Experience_Certificate.pdf")
                best_page_num = semantic_res.get("page_number", 1)

        if not matched_projects:
            return {
                "status": "FAIL" if mandatory else "REVIEW",
                "confidence": 0.90,
                "reason": "No verifiable Oil & Gas or Hydrocarbon sector project completion certificates found in submitted documents.",
                "evidence": "Missing required Oil & Gas domain credentials.",
                "document_id": None,
                "document_name": "Experience_Certificates.pdf",
                "page_number": 1,
                "source": "SEMANTIC_EXPERIENCE_MATCHER",
                "method": "NLP_DOMAIN_CLASSIFICATION",
                "calculation_breakdown": {
                    "domain": "Oil & Gas / Petroleum / Natural Gas",
                    "qualifying_projects_found": 0,
                    "requirement_met": False
                }
            }

        project_count = len(matched_projects)
        summary_keywords = list(set([kw for p in matched_projects for kw in p.get("keywords", [])]))
        
        return {
            "status": "PASS",
            "confidence": min(0.98, max(0.85, highest_confidence)),
            "reason": f"Bidder demonstrates verified experience in Petroleum/Oil & Gas sector across {project_count} project submission(s) ({', '.join(summary_keywords[:4])}).",
            "evidence": best_evidence or f"Verified {project_count} hydrocarbon/petroleum sector project execution certificate(s).",
            "document_id": best_doc_id,
            "document_name": best_doc_name,
            "page_number": best_page_num,
            "source": "SEMANTIC_EXPERIENCE_MATCHER",
            "method": "NLP_DOMAIN_CLASSIFICATION",
            "calculation_breakdown": {
                "domain": "Oil & Gas / Petroleum / Natural Gas",
                "qualifying_projects_found": project_count,
                "domain_indicators": summary_keywords[:5],
                "requirement_met": True
            }
        }
