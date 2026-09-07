"""
SIH26100 — FAISS Vector Indexing & Retrieval Service
----------------------------------------------------
Indexes bidder document evidence chunks in FAISS dense vector space
while preserving strict document and page provenance metadata.

Authoritative Path:
    ml/services/faiss_service.py
"""
import threading
from typing import List, Dict, Any, Optional
import numpy as np

try:
    from ml.services.embedding_service import embedding_service
except ImportError:
    from embedding_service import embedding_service


class FAISSEvidenceIndex:
    """
    FAISS-based vector index for bidder evidence chunks.
    Maintains synchronized metadata mapping across indexed chunks.
    """

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.metadata_store: List[Dict[str, Any]] = []
        self._index = None
        self._lock = threading.Lock()
        self._init_index()

    def _init_index(self):
        try:
            import faiss
            # Inner product on L2-normalized vectors is equivalent to cosine similarity
            self._index = faiss.IndexFlatIP(self.dimension)
            self._use_faiss = True
        except Exception:
            self._use_faiss = False
            self._vectors: List[np.ndarray] = []

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Indexes a list of evidence chunks.
        Each chunk must have:
            - chunk_id: str
            - document_id: str
            - document_name: str
            - page_number: int
            - text: str
            - extraction_method: str ('PDF_TEXT' or 'TESSERACT_OCR')
            - bidder_id: Optional[str]
            - category: Optional[str]
        """
        if not chunks:
            return 0

        with self._lock:
            texts = [c.get("text", "") for c in chunks]
            embeddings = embedding_service.embed_documents(texts)
            vectors = np.array(embeddings, dtype=np.float32)

            # Ensure L2 normalization
            faiss_norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            faiss_norms[faiss_norms == 0] = 1.0
            vectors = vectors / faiss_norms

            if self._use_faiss and self._index is not None:
                self._index.add(vectors)
            else:
                if not hasattr(self, "_vectors"):
                    self._vectors = []
                for v in vectors:
                    self._vectors.append(v)

            for chunk in chunks:
                self.metadata_store.append({
                    "chunk_id": chunk.get("chunk_id") or chunk.get("id", ""),
                    "document_id": chunk.get("document_id", ""),
                    "document_name": chunk.get("document_name", "Bidder_Document.pdf"),
                    "page_number": int(chunk.get("page_number", 1)),
                    "text": chunk.get("text", ""),
                    "extraction_method": chunk.get("extraction_method", "PDF_TEXT"),
                    "bidder_id": chunk.get("bidder_id", ""),
                    "category": chunk.get("category", ""),
                })

            return len(chunks)

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        bidder_id: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Searches the FAISS index with a normalized query vector and returns top_k evidence chunks.
        """
        with self._lock:
            if not self.metadata_store:
                return []

            q_vec = np.array([query_vector], dtype=np.float32)
            q_norm = np.linalg.norm(q_vec)
            if q_norm > 0:
                q_vec = q_vec / q_norm

            total_items = len(self.metadata_store)
            k_search = min(top_k * 3, total_items)  # fetch buffer for filtering

            results = []
            if self._use_faiss and self._index is not None and self._index.ntotal > 0:
                distances, indices = self._index.search(q_vec, k_search)
                for score, idx in zip(distances[0], indices[0]):
                    if idx < 0 or idx >= len(self.metadata_store):
                        continue
                    meta = self.metadata_store[idx]
                    
                    # Apply optional metadata filtering
                    if bidder_id and meta.get("bidder_id") and meta.get("bidder_id") != bidder_id:
                        continue
                    if category and meta.get("category") and meta.get("category") != category:
                        # soft category filter: penalty rather than hard exclude
                        score = score * 0.90

                    sim_score = max(0.0, min(1.0, round(float(score), 4)))
                    results.append({
                        "document_id": meta["document_id"],
                        "document_name": meta["document_name"],
                        "page_number": meta["page_number"],
                        "chunk_id": meta["chunk_id"],
                        "text": meta["text"],
                        "extraction_method": meta["extraction_method"],
                        "bidder_id": meta.get("bidder_id", ""),
                        "category": meta.get("category", ""),
                        "similarity_score": sim_score
                    })
            else:
                # Numpy fallback search
                if hasattr(self, "_vectors") and self._vectors:
                    all_vecs = np.array(self._vectors, dtype=np.float32)
                    sims = np.dot(all_vecs, q_vec.T).flatten()
                    sorted_indices = np.argsort(-sims)[:k_search]
                    for idx in sorted_indices:
                        meta = self.metadata_store[idx]
                        score = sims[idx]
                        if bidder_id and meta.get("bidder_id") and meta.get("bidder_id") != bidder_id:
                            continue
                        sim_score = max(0.0, min(1.0, round(float(score), 4)))
                        results.append({
                            "document_id": meta["document_id"],
                            "document_name": meta["document_name"],
                            "page_number": meta["page_number"],
                            "chunk_id": meta["chunk_id"],
                            "text": meta["text"],
                            "extraction_method": meta["extraction_method"],
                            "bidder_id": meta.get("bidder_id", ""),
                            "category": meta.get("category", ""),
                            "similarity_score": sim_score
                        })

            # Sort by similarity and return top_k
            results.sort(key=lambda x: x["similarity_score"], reverse=True)
            return results[:top_k]

    def index_documents(self, documents: List[Dict[str, Any]]) -> int:
        """
        Indexes documents / evidence chunks into the FAISS vector space.
        Alias for add_chunks supporting document list ingestion.
        """
        return self.add_chunks(documents)

    def save_index(self, path: str) -> bool:
        """Saves the FAISS index and metadata store to disk."""
        import os
        import json
        with self._lock:
            try:
                os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
                meta_path = f"{path}.meta.json"
                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump(self.metadata_store, f, indent=2)

                if self._use_faiss and self._index is not None:
                    import faiss
                    faiss.write_index(self._index, path)
                elif hasattr(self, "_vectors") and self._vectors:
                    np.save(path, np.array(self._vectors))
                return True
            except Exception:
                return False

    def load_index(self, path: str) -> bool:
        """Loads the FAISS index and metadata store from disk."""
        import os
        import json
        with self._lock:
            try:
                meta_path = f"{path}.meta.json"
                if os.path.exists(meta_path):
                    with open(meta_path, "r", encoding="utf-8") as f:
                        self.metadata_store = json.load(f)

                if os.path.exists(path):
                    if self._use_faiss:
                        import faiss
                        self._index = faiss.read_index(path)
                    else:
                        self._vectors = list(np.load(path))
                return True
            except Exception:
                return False

    def clear(self):
        """Resets the FAISS index and metadata store."""
        with self._lock:
            self.metadata_store = []
            self._init_index()

    def get_count(self) -> int:
        return len(self.metadata_store)


# Global index instance
faiss_evidence_index = FAISSEvidenceIndex()
faiss_service = faiss_evidence_index

