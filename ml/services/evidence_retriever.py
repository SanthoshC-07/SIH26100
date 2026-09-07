"""
SIH26100 — Requirement to Evidence Retrieval Service
---------------------------------------------------
Converts structured tender requirements into dense semantic queries,
retrieves relevant evidence chunks via FAISS vector search, and formats
evidence attribution with document name, page number, and similarity scores.

IMPORTANT COMPLIANCE SEPARATION:
Semantic similarity indicates RELEVANCE ONLY. It NEVER directly computes
PASS or FAIL decisions. Numeric and logical criteria are evaluated separately.

Authoritative Path:
    ml/services/evidence_retriever.py
"""
from typing import List, Dict, Any, Optional

try:
    from ml.services.embedding_service import embedding_service
    from ml.services.faiss_service import faiss_evidence_index
except ImportError:
    from embedding_service import embedding_service
    from faiss_service import faiss_evidence_index


class EvidenceRetrieverService:
    """
    Evidence retrieval orchestrator connecting structured requirements to bidder evidence chunks.
    """

    def __init__(self):
        self.embedding_service = embedding_service
        self.vector_index = faiss_evidence_index

    def retrieve_evidence_for_requirement(
        self,
        requirement_text: str,
        requirement_id: Optional[str] = None,
        bidder_id: Optional[str] = None,
        category: Optional[str] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Retrieves top matching evidence chunks for a given requirement.
        
        Returns:
            {
                "requirement_id": str,
                "requirement_text": str,
                "query": str,
                "category": str,
                "top_similarity": float,
                "evidence_status": "VERIFICATION_READY" | "REVIEW" | "NO_EVIDENCE",
                "evidence": [
                    {
                        "document_id": str,
                        "document_name": str,
                        "page_number": int,
                        "chunk_id": str,
                        "text": str,
                        "extraction_method": str,
                        "similarity_score": float
                    }
                ]
            }
        """
        if not requirement_text or not requirement_text.strip():
            return {
                "requirement_id": requirement_id or "",
                "requirement_text": "",
                "query": "",
                "category": category or "",
                "top_similarity": 0.0,
                "evidence_status": "NO_EVIDENCE",
                "evidence": []
            }

        # 1. Construct semantic query
        query = self._build_semantic_query(requirement_text, category)

        # 2. Generate dense query embedding
        query_vector = self.embedding_service.embed_text(query)

        # 3. Retrieve top-k chunks from FAISS
        chunks = self.vector_index.search(
            query_vector=query_vector,
            top_k=top_k,
            bidder_id=bidder_id,
            category=category
        )

        top_similarity = chunks[0]["similarity_score"] if chunks else 0.0

        # 4. Determine evidence status (relevance only, NEVER compliance decision)
        if not chunks:
            evidence_status = "NO_EVIDENCE"
        elif top_similarity >= 0.65:
            evidence_status = "VERIFICATION_READY"
        else:
            evidence_status = "REVIEW"

        return {
            "requirement_id": requirement_id or "REQ-UNSPECIFIED",
            "requirement_text": requirement_text,
            "query": query,
            "category": category or "",
            "top_similarity": top_similarity,
            "evidence_status": evidence_status,
            "message": "No matching evidence chunks found in index." if not chunks else f"Found {len(chunks)} relevant evidence chunks.",
            "evidence": chunks
        }

    def _build_semantic_query(self, requirement_text: str, category: Optional[str] = None) -> str:
        """Enriches the query with domain keywords for enhanced neural retrieval."""
        base = requirement_text.strip()
        if not category:
            return base

        domain_hints = {
            "GST_TAX_COMPLIANCE": "GSTIN registration certificate GSTR-3B filing",
            "MSME_UDYAM_ELIGIBILITY": "Udyam registration certificate MSME enterprise",
            "FINANCIAL_ELIGIBILITY": "audited balance sheet annual financial turnover net worth",
            "EXPERIENCE_ELIGIBILITY": "completion certificate cross country pipeline execution length",
            "OEM_AUTHORIZATION": "manufacturer authorization form MAF OEM warranty",
            "BLACKLISTING_DEBARMENT": "non blacklisting non debarment declaration affidavit",
            "TECHNICAL_SPECIFICATION": "line pipe diameter ASME B31.8 API 5L technical parameters",
            "INDUSTRY_STANDARD_COMPLIANCE": "API 6D API 1104 ASME OISD standard compliance report",
            "SAFETY_REGULATORY_COMPLIANCE": "ISO 45001 occupational health safety HSE policy",
            "MAKE_IN_INDIA_LOCAL_CONTENT": "local content declaration Make in India certificate"
        }

        hint = domain_hints.get(category, "")
        return f"{base} {hint}".strip()


evidence_retriever_service = EvidenceRetrieverService()
