from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.chunking import chunk_extracted_payload


def load_extracted_files(extracted_dir: Path) -> list[Path]:
    files = sorted(extracted_dir.glob("*.json"))
    assert files, "No extracted JSON files found. Run Phase 1 first."
    return files


def validate_chunk_order(text: str, chunks: list[dict]) -> None:
    last_start = 0
    for chunk in chunks:
        content = chunk["content"]
        index = text.find(content, last_start)
        assert index >= 0, "Chunk not found in original text."
        assert index >= last_start, "Chunk order is incorrect."
        last_start = index


def validate_sentence_boundaries(chunks: list[dict], chunk_size: int) -> None:
    for chunk in chunks[:-1]:
        content = chunk["content"].rstrip()
        ends_with_boundary = content.endswith((".", "!", "?", "\n"))
        if not ends_with_boundary and len(content) < chunk_size:
            raise AssertionError("Chunk does not end at a sentence boundary.")


def validate_overlap(chunks: list[dict], overlap: int) -> None:
    if overlap <= 0:
        return
    for left, right in zip(chunks, chunks[1:]):
        left_text = left["content"]
        right_text = right["content"]
        if len(left_text) < overlap or len(right_text) < overlap:
            continue
        overlap_text = left_text[-overlap:]
        assert overlap_text in right_text, "Chunk overlap not preserved."


def run_chunking_tests(chunk_size: int = 800, chunk_overlap: int = 100) -> None:
    extracted_dir = Path(__file__).resolve().parents[1] / "extracted"
    extracted_files = load_extracted_files(extracted_dir)

    for extracted_file in extracted_files:
        payload = extracted_file.read_text(encoding="utf-8")
        data = __import__("json").loads(payload)
        source = data.get("filename", extracted_file.stem)
        text = data.get("extracted_text", "")

        chunks, metadata = chunk_extracted_payload(
            data,
            source=source,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        print(f"\n{source} chunk sizes:")
        for chunk in chunks:
            print(f"  chunk {chunk['chunk_id']}: {len(chunk['content'])}")

        validate_chunk_order(text, chunks)
        validate_sentence_boundaries(chunks, chunk_size)
        validate_overlap(chunks, chunk_overlap)

        assert metadata["chunk_count"] == len(chunks)


if __name__ == "__main__":
    run_chunking_tests()
    print("All Phase 2 chunking tests passed.")
