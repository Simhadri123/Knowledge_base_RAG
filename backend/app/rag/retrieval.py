from __future__ import annotations

import logging
from typing import Dict, List

import numpy as np

from .embedding import LocalEmbedder

logger = logging.getLogger("rag.retrieval")


def retrieve(
    query: str,
    index,
    metadata: List[Dict],
    embedder: LocalEmbedder,
    top_k: int = 5,
) -> List[Dict]:
    query_vec = embedder.embed_query(query)
    query_vec = np.expand_dims(query_vec, axis=0)

    scores, indices = index.search(query_vec, top_k)
    results: List[Dict] = []
    for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), start=1):
        if idx < 0 or idx >= len(metadata):
            continue
        chunk = metadata[idx]
        chunk_result = {
            **chunk,
            "score": float(score),
            "rank": rank,
        }
        results.append(chunk_result)

    logger.info("Retrieved %s chunks for query", len(results))
    for item in results:
        logger.info("Rank %s score %.4f section %s", item["rank"], item["score"], item["section"])

    return results
