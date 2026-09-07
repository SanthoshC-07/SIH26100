"""
Vector Store & Evidence Retrieval Index
Ministry of Petroleum & Natural Gas - Petroleum & Natural Gas Pipeline Procurement
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.models import EvidenceChunk, Document, Requirement
from app.ml.embeddings import embedding_engine
from app.nlp.text_normalizer import TextNormalizer
from app.core.logging_config import logger

class VectorStore:
    """
    Evidence retrieval vector store supporting search by requirement_id,
    semantic similarity query, and category filters with document & page attribution.
    """

    @classmethod
    def search_evidence_for_requirement(
        cls,
        db: Session,
        requirement_id: Optional[str] = None,
        bidder_id: Optional[str] = None,
        query: str = "",
        top_k: int = 5,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes semantic vector search over stored evidence chunks.
        """
        # 1. If requirement_id is provided, fetch requirement description for query context
        effective_query = query
        req_category = category
        if requirement_id:
            req = db.query(Requirement).filter(Requirement.id == requirement_id).first()
            if req:
                if not effective_query:
                    effective_query = f"{req.description} {req.normalized_requirement or ''} {req.category}"
                if not req_category:
                    req_category = req.category

        # 2. Query EvidenceChunks from database
        chunk_query = db.query(EvidenceChunk)
        if bidder_id:
            chunk_query = chunk_query.filter(EvidenceChunk.bidder_id == bidder_id)
        if req_category:
            chunk_query = chunk_query.filter(EvidenceChunk.category == req_category)

        db_chunks = chunk_query.all()
        
        # If category filter yielded nothing, fallback to all bidder chunks
        if not db_chunks and bidder_id:
            db_chunks = db.query(EvidenceChunk).filter(EvidenceChunk.bidder_id == bidder_id).all()

        # If still empty, build chunks from DocumentPages on the fly
        corpus_items = []
        if db_chunks:
            for c in db_chunks:
                doc = db.query(Document).filter(Document.id == c.document_id).first()
                corpus_items.append({
                    "chunk_id": c.id,
                    "document_id": c.document_id,
                    "document_name": doc.document_name if doc else "Evidence_Document.pdf",
                    "page_number": c.page_number,
                    "text": c.text,
                    "normalized_text": c.normalized_text,
                    "extraction_method": getattr(doc, "extraction_method", "PDF_TEXT") if doc else "PDF_TEXT",
                    "confidence": c.confidence or 0.95
                })
        else:
            # Fetch all documents for bidder
            doc_query = db.query(Document)
            if bidder_id:
                doc_query = doc_query.filter(Document.bidder_id == bidder_id)
            docs = doc_query.all()
            for doc in docs:
                for page in doc.pages:
                    corpus_items.append({
                        "document_id": doc.id,
                        "document_name": doc.document_name,
                        "page_number": page.page_number,
                        "text": page.page_text or "",
                        "normalized_text": page.normalized_text or TextNormalizer.normalize_text(page.page_text or ""),
                        "extraction_method": page.extraction_method or "PDF_TEXT",
                        "confidence": page.confidence or 0.95
                    })

        if not corpus_items or not effective_query:
            return []

        # 3. Perform semantic retrieval ranking
        ranked_results = embedding_engine.retrieve_top_evidence(effective_query, corpus_items, top_k=top_k)

        formatted_results = []
        for item, score in ranked_results:
            formatted_results.append({
                "document_id": item.get("document_id", ""),
                "document_name": item.get("document_name", "Evidence.pdf"),
                "page_number": item.get("page_number", 1),
                "text": item.get("text", ""),
                "normalized_text": item.get("normalized_text", ""),
                "similarity_score": round(score, 4),
                "confidence": item.get("confidence", 0.95),
                "extraction_method": item.get("extraction_method", "PDF_TEXT"),
                "extracted_entities": {}
            })

        return formatted_results

vector_store = VectorStore()
