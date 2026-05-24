from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

import faiss

from .embedding import LocalEmbedder

logger = logging.getLogger("rag.indexing")


def build_index(
    chunks: List[Dict],
    embedder: LocalEmbedder,
    vector_dir: Path,
) -> Tuple[faiss.IndexFlatIP, Path]:
    vector_dir = Path(vector_dir)
    vector_dir.mkdir(parents=True, exist_ok=True)

    texts = [chunk["content"] for chunk in chunks]
    embeddings = embedder.embed_texts(texts)

    dim = embedder.dimension()
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    index_path = vector_dir / "kb.index.faiss"
    meta_path = vector_dir / "kb.metadata.json"

    faiss.write_index(index, str(index_path))
    meta_path.write_text(json.dumps(chunks, indent=2), encoding="utf-8")

    logger.info("FAISS index built: %s vectors", index.ntotal)
    logger.info("Index saved: %s", index_path)
    logger.info("Metadata saved: %s", meta_path)

    return index, meta_path


def load_index(vector_dir: Path) -> Tuple[faiss.IndexFlatIP, List[Dict]]:
    vector_dir = Path(vector_dir)
    index_path = vector_dir / "kb.index.faiss"
    meta_path = vector_dir / "kb.metadata.json"

    if not index_path.exists() or not meta_path.exists():
        raise FileNotFoundError("Vector index or metadata not found")

    index = faiss.read_index(str(index_path))
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))

    logger.info("FAISS index loaded: %s vectors", index.ntotal)
    logger.info("Metadata loaded: %s entries", len(metadata))

    return index, metadata
