from pathlib import Path
import sys
import logging
import json

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.rag.chunking import build_chunks
from app.rag.embedding import LocalEmbedder
from app.rag.indexing import build_index, load_index
import os

from app.rag.chatbot import answer_query

logging.basicConfig(level=logging.INFO)


def main() -> None:
    if not os.getenv("OPENROUTER_API_KEY"):
        print("OPENROUTER_API_KEY not set. Skipping chatbot test.")
        return
    kb_dir = BASE_DIR / "knowledge_base"
    kb_dir.mkdir(parents=True, exist_ok=True)
    if not list(kb_dir.glob("*.json")):
        sample = {
            "title": "Sample KB Article",
            "content": "## Abstract\nSample content.\n\n## Methodology\nSample steps.",
        }
        (kb_dir / "sample_kb.json").write_text(
            json.dumps(sample, indent=2),
            encoding="utf-8",
        )
    vector_dir = BASE_DIR / "vector_store"
    chunks = build_chunks(kb_dir)
    embedder = LocalEmbedder()
    build_index(chunks, embedder, vector_dir)

    index, metadata = load_index(vector_dir)
    query = "What is the methodology?"
    result = answer_query(query, index, metadata, embedder)

    print("\n--- Retrieved Context ---")
    for item in result["retrieved"]:
        print(f"[{item['section']}] score={item['score']:.4f}")
        print(item["content"][:300])

    print("\n--- Final Response ---")
    print(result["response"])


if __name__ == "__main__":
    main()
