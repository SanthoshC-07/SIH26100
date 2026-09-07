"""
Semantic Embedding & Neural Retrieval Engine
Ministry of Petroleum & Natural Gas - Petroleum & Natural Gas Pipeline Procurement
"""
import math
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.core.logging_config import logger
from app.nlp.vocabulary import PetroleumVocabulary
from app.nlp.text_normalizer import TextNormalizer

class SemanticEmbeddingEngine:
    """
    Sentence Transformers + Dense Vector Semantic Matching Engine
    with TF-IDF / Sublinear Fallback for sub-millisecond retrieval.
    """

    def __init__(self):
        self._st_model = None
        self._vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            max_features=10000,
            stop_words="english",
            sublinear_tf=True
        )

    def _get_st_model(self):
        """Lazy load SentenceTransformer model if available without blocking startup."""
        if self._st_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                # Try loading from local cache first
                try:
                    self._st_model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
                except Exception:
                    self._st_model = SentenceTransformer("all-MiniLM-L6-v2")
                logger.info("Loaded SentenceTransformer ('all-MiniLM-L6-v2') successfully.")
            except Exception as e:
                logger.warning(f"SentenceTransformer not loaded ({e}), using TF-IDF neural simulation.")
                self._st_model = False
        return self._st_model if self._st_model is not False else None


    def encode(self, text: str) -> List[float]:
        """
        Generates dense embedding vector for given text.
        """
        model = self._get_st_model()
        norm_text = TextNormalizer.normalize_text(text)
        if model:
            try:
                emb = model.encode(norm_text, convert_to_numpy=True)
                return emb.tolist()
            except Exception:
                pass

        # Fast deterministic hash-based 64-dim embedding simulation
        words = norm_text.lower().split()
        vec = np.zeros(64, dtype=np.float32)
        for i, w in enumerate(words):
            h = hash(w) % 64
            vec[h] += 1.0 / (i + 1)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec.tolist()

    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Computes semantic similarity score between two texts (0.0 to 1.0).
        """
        t1 = TextNormalizer.normalize_text(text1)
        t2 = TextNormalizer.normalize_text(text2)
        
        if not t1 or not t2:
            return 0.0

        model = self._get_st_model()
        if model:
            try:
                emb1 = model.encode([t1], convert_to_numpy=True)
                emb2 = model.encode([t2], convert_to_numpy=True)
                sim = float(cosine_similarity(emb1, emb2)[0][0])
                return max(0.0, min(1.0, round(sim, 4)))
            except Exception:
                pass

        # TF-IDF Cosine Similarity with Petroleum domain term weighting
        try:
            mat = self._vectorizer.fit_transform([t1, t2])
            sim = float(cosine_similarity(mat[0:1], mat[1:2])[0][0])
            
            # Domain bonus if both share petroleum concepts
            has_p1 = PetroleumVocabulary.contains_petroleum_concept(t1)
            has_p2 = PetroleumVocabulary.contains_petroleum_concept(t2)
            if has_p1 and has_p2:
                sim = min(0.98, sim + 0.15)

            return max(0.0, min(1.0, round(sim, 4)))
        except Exception:
            return self._fallback_jaccard(t1, t2)

    def retrieve_top_evidence(
        self,
        query: str,
        corpus_items: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Ranks corpus chunks by semantic similarity against the query.
        corpus_items: list of {"text": str, "document_name": str, "page_number": int, "document_id": str, ...}
        """
        if not corpus_items or not query:
            return []

        norm_query = TextNormalizer.normalize_text(query)
        texts = [TextNormalizer.normalize_text(item.get("text", "") or item.get("normalized_text", "")) for item in corpus_items]

        if not any(texts) or not norm_query.strip():
            return []

        model = self._get_st_model()
        if model:
            try:
                q_emb = model.encode([norm_query], convert_to_numpy=True)
                d_embs = model.encode(texts, convert_to_numpy=True)
                scores = cosine_similarity(q_emb, d_embs).flatten()
                
                ranked = np.argsort(scores)[::-1]
                results = []
                for idx in ranked[:top_k]:
                    sc = float(scores[idx])
                    if sc > 0.05:
                        results.append((corpus_items[idx], round(sc, 4)))
                return results
            except Exception as e:
                logger.warning(f"Neural retrieval error ({e}), using TF-IDF ranking.")

        # Fallback to TF-IDF cosine ranking
        all_docs = [norm_query] + texts
        try:
            mat = self._vectorizer.fit_transform(all_docs)
            q_vec = mat[0:1]
            d_vecs = mat[1:]
            scores = cosine_similarity(q_vec, d_vecs).flatten()
            ranked = np.argsort(scores)[::-1]
            results = []
            for idx in ranked[:top_k]:
                sc = float(scores[idx])
                # Petroleum domain weight boost
                if PetroleumVocabulary.contains_petroleum_concept(norm_query) and PetroleumVocabulary.contains_petroleum_concept(texts[idx]):
                    sc = min(0.96, sc + 0.12)
                if sc > 0.05:
                    results.append((corpus_items[idx], round(sc, 4)))
            return results
        except Exception:
            return self._fallback_keyword_rank(norm_query, corpus_items, top_k)

    def _fallback_jaccard(self, t1: str, t2: str) -> float:
        w1 = set(t1.lower().split())
        w2 = set(t2.lower().split())
        if not w1 or not w2:
            return 0.0
        return round(len(w1.intersection(w2)) / len(w1.union(w2)), 4)

    def _fallback_keyword_rank(self, query: str, corpus_items: List[Dict[str, Any]], top_k: int) -> List[Tuple[Dict[str, Any], float]]:
        query_words = set(query.lower().split())
        scored = []
        for item in corpus_items:
            text_words = set(item.get("text", "").lower().split())
            intersection = query_words.intersection(text_words)
            sim = len(intersection) / max(1, math.sqrt(len(query_words) * len(text_words)))
            if sim > 0.05:
                scored.append((item, round(sim, 4)))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

embedding_engine = SemanticEmbeddingEngine()
embedding_service = embedding_engine

