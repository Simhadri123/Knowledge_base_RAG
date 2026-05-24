from pathlib import Path
import sys
import logging
import json

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.rag.chunking import build_chunks
from app.rag.embedding import LocalEmbedder

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
    chunks = build_chunks(kb_dir)
    embedder = LocalEmbedder()
    vectors = embedder.embed_texts([chunk["content"] for chunk in chunks])
    print("Embedding shape:", vectors.shape)
    assert vectors.shape[0] == len(chunks)


if __name__ == "__main__":
    main()
