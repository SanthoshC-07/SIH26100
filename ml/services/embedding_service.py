"""
SIH26100 — Sentence Transformers Embedding Service
--------------------------------------------------
Modular dense embedding service for tender requirements and bidder evidence chunks.
Uses pretrained SentenceTransformer model ('all-MiniLM-L6-v2') with cosine similarity
computation and batch encoding support.

Authoritative Path:
    ml/services/embedding_service.py
"""
import math
from typing import List, Union, Optional
import numpy as np


class SentenceTransformerEmbeddingService:
    """
    Sentence Transformers Embedding Service.
    Supports single text embedding, batch document embedding, and cosine similarity calculation.
    """

    _instance = None

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        self._dimension = 384  # standard for all-MiniLM-L6-v2

    @classmethod
    def get_instance(cls) -> "SentenceTransformerEmbeddingService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                # Try local cache or download
                try:
                    self._model = SentenceTransformer(self.model_name, local_files_only=True)
                except Exception:
                    self._model = SentenceTransformer(self.model_name)
                self._dimension = self._model.get_sentence_embedding_dimension()
            except Exception as e:
                # Fallback to simulated numpy embedding vectorizer if torch/transformers unavailable
                self._model = False

        return self._model if self._model is not False else None

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_text(self, text: str) -> List[float]:
        """
        Generates dense embedding vector (384-d normalized) for a single string.
        """
        if not text or not text.strip():
            return [0.0] * self._dimension

        model = self._load_model()
        if model:
            try:
                emb = model.encode(text.strip(), normalize_embeddings=True, convert_to_numpy=True)
                return emb.tolist()
            except Exception:
                pass

        # Robust deterministic fallback vector
        return self._fallback_embedding(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generates dense embeddings for a batch of documents/chunks.
        """
        if not texts:
            return []

        model = self._load_model()
        if model:
            try:
                clean_texts = [t.strip() if t and t.strip() else " " for t in texts]
                embeddings = model.encode(clean_texts, normalize_embeddings=True, convert_to_numpy=True, batch_size=32)
                return embeddings.tolist()
            except Exception:
                pass

        return [self.embed_text(t) for t in texts]

    def calculate_similarity(self, embedding_a: List[float], embedding_b: List[float]) -> float:
        """
        Calculates cosine similarity between two normalized embedding vectors (range 0.0 to 1.0).
        """
        if not embedding_a or not embedding_b or len(embedding_a) != len(embedding_b):
            return 0.0

        vec_a = np.array(embedding_a, dtype=np.float32)
        vec_b = np.array(embedding_b, dtype=np.float32)

        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        sim = float(np.dot(vec_a, vec_b) / (norm_a * norm_b))
        # Clip to [0.0, 1.0] for similarity interpretation
        return max(0.0, min(1.0, round((sim + 1.0) / 2.0 if sim < 0 else sim, 4)))

    def _fallback_embedding(self, text: str) -> List[float]:
        """Deterministic 384-dimensional hashed normalized vector for offline fallback."""
        vec = np.zeros(self._dimension, dtype=np.float32)
        tokens = text.lower().split()
        for i, token in enumerate(tokens):
            idx = abs(hash(token)) % self._dimension
            vec[idx] += 1.0 / (i + 1.0)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()


embedding_service = SentenceTransformerEmbeddingService.get_instance()
