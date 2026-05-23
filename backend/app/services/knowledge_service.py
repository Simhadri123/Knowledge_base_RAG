import json
from datetime import datetime
from pathlib import Path
from typing import Dict

from ..config import EXTRACTED_DIR
from ..knowledge import generate_explanation_auto
from ..storage import save_knowledge_json


def _build_response(
    source: str,
    result,
    raw: str,
    steps,
    chunk_count: int,
) -> Dict:
    return {
        "source": source,
        "title": result.title,
        "content": result.content,
        "raw_response": raw,
        "chunk_count": chunk_count,
        "step_outputs": steps,
    }


def generate_from_text(
    text: str,
    source: str,
    chunk_size: int,
    chunk_overlap: int,
    max_parts: int,
    save_output: bool,
) -> Dict:
    if not text.strip():
        raise ValueError("Text is empty")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    result, raw, steps, chunks = generate_explanation_auto(
        text,
        source=source,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        max_parts=max_parts,
        save_output=save_output,
    )
    return _build_response(source, result, raw, steps, len(chunks))


def generate_from_extracted(
    extracted_filename: str,
    chunk_size: int,
    chunk_overlap: int,
    max_parts: int,
    save_output: bool,
) -> Dict:
    extracted_path = EXTRACTED_DIR / extracted_filename
    if not extracted_path.exists():
        raise FileNotFoundError(f"Extracted file not found: {extracted_filename}")

    data = json.loads(extracted_path.read_text(encoding="utf-8"))
    text = data.get("extracted_text", "")
    if not text.strip():
        raise ValueError("Extracted text is empty")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    source = data.get("filename", extracted_path.stem)
    result, raw, steps, chunks = generate_explanation_auto(
        text,
        source=source,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        max_parts=max_parts,
        save_output=save_output,
    )
    return _build_response(source, result, raw, steps, len(chunks))


def approve_knowledge(source: str, title: str, content: str) -> Dict:
    if not content.strip():
        raise ValueError("Knowledge content is empty")
    if not title.strip():
        raise ValueError("Knowledge title is empty")

    payload = {
        "source": source,
        "title": title,
        "content": content,
        "approved_at": datetime.utcnow().isoformat() + "Z",
    }
    saved_path = save_knowledge_json(source, payload)
    return {"source": source, "saved_path": str(saved_path)}
