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

    index, meta_path = build_index(chunks, embedder, vector_dir)
    print("Index vectors:", index.ntotal)
    print("Metadata path:", meta_path)

    index2, metadata = load_index(vector_dir)
    print("Reloaded vectors:", index2.ntotal)
    assert index2.ntotal == len(metadata)


if __name__ == "__main__":
    main()
