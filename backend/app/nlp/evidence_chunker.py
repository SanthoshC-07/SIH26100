"""
Bidder Evidence Chunker
Ministry of Petroleum & Natural Gas - Petroleum & Natural Gas Pipeline Procurement
"""
import uuid
import re
from typing import List, Dict, Any, Optional
from app.nlp.text_normalizer import TextNormalizer
from app.nlp.vocabulary import PetroleumVocabulary

class EvidenceChunker:
    """
    Splits bidder evidence document pages into semantic chunks
    with page retention, category tagging, and normalized representations.
    """

    @classmethod
    def chunk_document_pages(
        cls,
        document_id: str,
        pages_data: List[Dict[str, Any]],
        bidder_id: Optional[str] = None,
        requirement_id: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Produces semantic chunks from list of page dictionaries.
        pages_data: list of {"page_number": int, "text": str, "raw_text": str, "normalized_text": str}
        """
        chunks = []
        chunk_idx = 0

        for page in pages_data:
            page_num = page.get("page_number", 1)
            raw_text = page.get("raw_text") or page.get("text", "")
            if not raw_text or not raw_text.strip():
                continue

            # Split page into logical paragraphs / sections
            paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
            if not paragraphs:
                paragraphs = [raw_text.strip()]

            for p in paragraphs:
                if len(p) < 20:  # Skip trivial fragments
                    continue

                norm_p = TextNormalizer.normalize_text(p)
                
                # Determine relevant domain category if not provided
                chunk_category = category
                if not chunk_category:
                    chunk_category = cls._detect_chunk_category(norm_p)

                chunk_record = {
                    "id": str(uuid.uuid4()),
                    "document_id": document_id,
                    "bidder_id": bidder_id,
                    "requirement_id": requirement_id,
                    "page_number": page_num,
                    "chunk_index": chunk_idx,
                    "text": p,
                    "raw_text": p,
                    "normalized_text": norm_p,
                    "category": chunk_category,
                    "confidence": 0.95,
                    "similarity_score": 0.0,
                    "metadata_payload": {
                        "has_petroleum_terms": PetroleumVocabulary.contains_petroleum_concept(norm_p),
                        "char_length": len(p),
                        "word_count": len(p.split())
                    }
                }
                chunks.append(chunk_record)
                chunk_idx += 1

        return chunks

    @classmethod
    def _detect_chunk_category(cls, text: str) -> Optional[str]:
        lower = text.lower()
        if "gst" in lower or "gstin" in lower:
            return "GST"
        if "pan" in lower or "income tax" in lower:
            return "PAN"
        if "turnover" in lower or "balance sheet" in lower or "profit and loss" in lower:
            return "TURNOVER"
        if "similar pipeline" in lower or ("pipeline" in lower and any(w in lower for w in ["km", "diameter", "transmission", "cross-country"])):
            return "SIMILAR_PIPELINE_EXPERIENCE"
        if "oil & gas" in lower or "petroleum" in lower or "hydrocarbon" in lower:
            return "OIL_GAS_EXPERIENCE"
        if "engineer" in lower or "personnel" in lower or "manpower" in lower or "b.tech" in lower:
            return "TECHNICAL_MANPOWER"
        if "iso 45001" in lower or "iso 14001" in lower or "safety" in lower:
            return "HSE_SAFETY"
        if "local content" in lower or "make in india" in lower:
            return "LOCAL_CONTENT"
        return None
