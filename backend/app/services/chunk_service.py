import json
from pathlib import Path
from typing import Dict, List, Tuple

from ..chunking import chunk_extracted_payload, chunk_text
from ..config import EXTRACTED_DIR
from ..storage import save_chunks_json


def _build_metadata(chunk_size: int, chunk_overlap: int, count: int) -> Dict:
    return {
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "chunk_count": count,
    }


def chunk_from_text(
    text: str,
    source: str,
    chunk_size: int,
    chunk_overlap: int,
    save: bool,
) -> Dict:
    if not text.strip():
        raise ValueError("Text is empty")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks = chunk_text(
        text,
        source=source,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    metadata = _build_metadata(chunk_size, chunk_overlap, len(chunks))

    saved_path = None
    if save:
        payload = {
            "source": source,
            "chunks": chunks,
            "metadata": metadata,
        }
        saved_path = str(save_chunks_json(source, payload))

    return {
        "source": source,
        "chunks": chunks,
        "metadata": metadata,
        "saved_path": saved_path,
    }


def chunk_from_extracted(
    extracted_filename: str,
    chunk_size: int,
    chunk_overlap: int,
    save: bool,
) -> Dict:
    extracted_path = EXTRACTED_DIR / extracted_filename
    if not extracted_path.exists():
        raise FileNotFoundError(f"Extracted file not found: {extracted_filename}")

    data = json.loads(extracted_path.read_text(encoding="utf-8"))
    source = data.get("filename", extracted_path.stem)
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")
    chunks, metadata = chunk_extracted_payload(
        data,
        source=source,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    saved_path = None
    if save:
        payload = {
            "source": source,
            "chunks": chunks,
            "metadata": metadata,
        }
        saved_path = str(save_chunks_json(extracted_filename, payload))

    return {
        "source": source,
        "chunks": chunks,
        "metadata": metadata,
        "saved_path": saved_path,
    }
