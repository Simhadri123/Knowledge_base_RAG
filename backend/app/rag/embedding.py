from __future__ import annotations

import logging
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger("rag.embedding")


class LocalEmbedder:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        logger.info("Loaded embedding model: %s", model_name)

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        logger.info("Generating embeddings for %s chunks", len(texts))
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return np.asarray(embeddings, dtype="float32")

    def embed_query(self, text: str) -> np.ndarray:
        embedding = self.model.encode([text], normalize_embeddings=True)[0]
        return np.asarray(embedding, dtype="float32")

    def dimension(self) -> int:
        return int(self.model.get_sentence_embedding_dimension())
