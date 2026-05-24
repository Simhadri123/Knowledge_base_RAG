import logging
from pathlib import Path
from typing import Dict

from ..db.session import SessionLocal
from ..rag.embedding import LocalEmbedder
from ..rag.indexing import load_index
from ..rag.retrieval import retrieve
from ..rag.chatbot import answer_query
from ..services.vector_store_service import sync_vector_store

logger = logging.getLogger("chatbot.service")


def _ensure_index(vector_dir: Path) -> tuple | None:
    try:
        index, metadata = load_index(vector_dir)
        return index, metadata
    except FileNotFoundError:
        logger.info("Vector store not found. Syncing from published KBs.")

    with SessionLocal() as db:
        sync_vector_store(db, vector_dir)

    try:
        return load_index(vector_dir)
    except FileNotFoundError:
        return None


def query_chatbot(
    query: str,
    top_k: int,
    min_score: float,
    model: str,
    debug_prompt: bool,
) -> Dict:
    if not query.strip():
        raise ValueError("Query is empty")

    base_dir = Path(__file__).resolve().parents[2]
    vector_dir = base_dir / "vector_store"

    index_bundle = _ensure_index(vector_dir)
    if not index_bundle:
        return {
            "query": query,
            "answer": "No relevant content found in the knowledge base.",
            "retrieved": [],
            "used_context": False,
            "debug_prompt": None,
        }

    index, metadata = index_bundle
    embedder = LocalEmbedder()
    retrieved = retrieve(query, index, metadata, embedder, top_k=top_k)

    if not retrieved or retrieved[0]["score"] < min_score:
        return {
            "query": query,
            "answer": "No relevant content found in the knowledge base.",
            "retrieved": [],
            "used_context": False,
            "debug_prompt": None,
        }

    result = answer_query(
        query=query,
        index=index,
        metadata=metadata,
        embedder=embedder,
        model=model,
        top_k=top_k,
    )

    response = {
        "query": query,
        "answer": result["response"],
        "retrieved": result["retrieved"],
        "used_context": True,
    }
    if debug_prompt:
        response["debug_prompt"] = result["prompt"]
    return response
