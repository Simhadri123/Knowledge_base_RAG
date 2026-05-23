from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.knowledge import generate_explanation_auto

SUPPORTED_DIRECT_TEXT = {".txt"}


def _load_text_from_path(path: Path) -> tuple[str, str]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        payload = __import__("json").loads(path.read_text(encoding="utf-8"))
        return path.name, payload.get("extracted_text", "")
    if suffix in SUPPORTED_DIRECT_TEXT:
        return path.name, path.read_text(encoding="utf-8", errors="ignore")

    from app.extraction import extract_text

    text, _metadata = extract_text(path)
    return path.name, text


def load_text_for_testing() -> tuple[str, str]:
    if len(sys.argv) > 1:
        input_path = Path(sys.argv[1]).expanduser().resolve()
        if not input_path.exists():
            raise FileNotFoundError(f"Missing input file: {input_path}")
        return _load_text_from_path(input_path)

    source_path = (
        BASE_DIR.parent
        / "LangChain Explained in 10 Minutes (Components Breakdown + Build Your First AI Chatbot).txt"
    )
    if not source_path.exists():
        raise FileNotFoundError(f"Missing test file: {source_path}")
    text = source_path.read_text(encoding="utf-8", errors="ignore")
    return source_path.name, text


def compare_chunk_to_explanation(chunk_text: str, explanation: str) -> float:
    chunk_words = {word.lower() for word in chunk_text.split() if len(word) > 4}
    explanation_words = {word.lower() for word in explanation.split() if len(word) > 4}
    if not chunk_words:
        return 0.0
    overlap = chunk_words.intersection(explanation_words)
    return len(overlap) / len(chunk_words)


def run_phase3_tests() -> None:
    source, text = load_text_for_testing()
    result, raw, steps, chunks = generate_explanation_auto(text, source=source)
    print(f"\nProcessing {source} with {len(chunks)} chunks")
    print("\nFinal refined output:\n", raw)

    previous_context = ""
    for chunk, step_output in zip(chunks, steps):
        print("\n--- Debug ---")
        print("Current chunk:\n", chunk["content"])
        print("Previous context:\n", previous_context)
        print("Refined output:\n", step_output)
        previous_context = step_output
        overlap_score = compare_chunk_to_explanation(chunk["content"], step_output)
        print(f"Chunk overlap score: {overlap_score:.2f}")

    assert result.content.strip(), "Empty knowledge base content"
    assert result.title.strip() or result.content.strip()


if __name__ == "__main__":
    run_phase3_tests()
    print("All Phase 3 knowledge extraction tests completed.")
