from pathlib import Path
import sys
import logging
import json

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.rag.chunking import build_chunks

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
    for chunk in chunks:
        print("\n--- Chunk ---")
        print("KB:", chunk["kb_id"])
        print("Title:", chunk["title"])
        print("Section:", chunk["section"])
        print(chunk["content"][:400])
    assert chunks, "No chunks generated"


if __name__ == "__main__":
    main()
