from typing import Dict, Any, List, Optional
from app.ml.embeddings import embedding_engine
from app.core.config import settings

class SemanticComplianceMatcher:
    """
    Evaluates semantic document evidence against structured tender clauses.
    Produces compliance classification (COMPLIANT, NON_COMPLIANT, INSUFFICIENT)
    along with confidence gating and model abstention logic.
    """

    @staticmethod
    def match_evidence(
        requirement_desc: str,
        document_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Searches bidder documents for evidence matching the requirement.
        Applies confidence gating:
          Confidence >= 0.90 -> High Confidence PASS
          0.70 <= Confidence < 0.90 -> REVIEW Recommended
          < 0.70 -> REVIEW Required (Model Abstention)
        """
        top_matches = embedding_engine.retrieve_top_evidence(requirement_desc, document_chunks, top_k=2)

        if not top_matches:
            return {
                "classification": "INSUFFICIENT",
                "confidence": 0.40,
                "evidence_snippet": "No relevant document evidence found for this clause.",
                "document_id": None,
                "document_name": None,
                "page_number": 1,
                "gated_status": "REVIEW"
            }

        best_item, sim_score = top_matches[0]
        text_snippet = best_item.get("text", "")[:350]
        
        # Base confidence calculation
        confidence = min(0.98, max(0.50, sim_score * 1.5 + 0.45))
        
        # Confidence Gating logic
        if confidence >= settings.CONFIDENCE_HIGH:
            gated_status = "PASS"
            classification = "COMPLIANT"
        elif confidence >= settings.CONFIDENCE_MEDIUM:
            gated_status = "REVIEW"
            classification = "COMPLIANT"
        else:
            gated_status = "REVIEW"
            classification = "INSUFFICIENT"

        return {
            "classification": classification,
            "confidence": round(confidence, 2),
            "evidence_snippet": text_snippet,
            "document_id": best_item.get("document_id"),
            "document_name": best_item.get("document_name"),
            "page_number": best_item.get("page_number", 1),
            "gated_status": gated_status
        }
