import math
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SemanticEmbeddingEngine:
    """
    Semantic Retrieval and Embedding Engine.
    Provides fast vector search, cosine similarity ranking,
    and evidence retrieval over document pages and paragraphs.
    Designed with a modular architecture so deep sentence-transformer models
    (e.g., all-MiniLM-L6-v2) can be plugged in.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            max_features=5000,
            stop_words="english",
            sublinear_tf=True
        )

    def retrieve_top_evidence(
        self,
        query: str,
        corpus_items: List[Dict[str, Any]],
        top_k: int = 3
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Retrieves the top-k most relevant evidence text chunks for a given requirement query.
        corpus_items: list of {"text": str, "document_name": str, "page_number": int, "document_id": str}
        """
        if not corpus_items or not query:
            return []

        texts = [item.get("text", "") for item in corpus_items]
        # Check if all texts are empty
        if not any(texts) or not query.strip():
            return []

        all_docs = [query] + texts
        try:
            tfidf_matrix = self.vectorizer.fit_transform(all_docs)
            query_vec = tfidf_matrix[0:1]
            doc_vecs = tfidf_matrix[1:]

            scores = cosine_similarity(query_vec, doc_vecs).flatten()
            
            ranked_indices = np.argsort(scores)[::-1]
            results = []
            
            for idx in ranked_indices[:top_k]:
                score = float(scores[idx])
                if score > 0.05: # Minimum relevance threshold
                    results.append((corpus_items[idx], score))
                    
            return results
        except Exception:
            # Fallback simple keyword match
            return self._fallback_keyword_rank(query, corpus_items, top_k)

    def _fallback_keyword_rank(self, query: str, corpus_items: List[Dict[str, Any]], top_k: int) -> List[Tuple[Dict[str, Any], float]]:
        query_words = set(query.lower().split())
        scored = []
        for item in corpus_items:
            text_words = set(item.get("text", "").lower().split())
            intersection = query_words.intersection(text_words)
            sim = len(intersection) / max(1, math.sqrt(len(query_words) * len(text_words)))
            if sim > 0.05:
                scored.append((item, sim))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

embedding_engine = SemanticEmbeddingEngine()
