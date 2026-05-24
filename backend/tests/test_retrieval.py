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
from app.rag.retrieval import retrieve

logging.basicConfig(level=logging.INFO)


def main() -> None:
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
    results = retrieve("What is the methodology?", index, metadata, embedder, top_k=3)
    for item in results:
        print("\n--- Retrieved ---")
        print("Score:", item["score"])
        print("Section:", item["section"])
        print(item["content"][:300])
    assert results, "No retrieval results"


if __name__ == "__main__":
    main()
