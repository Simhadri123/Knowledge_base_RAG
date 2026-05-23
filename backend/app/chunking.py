from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

from langchain_text_splitters import RecursiveCharacterTextSplitter

from .storage import save_chunks_json


def build_splitter(chunk_size: int, chunk_overlap: int) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " ", ""],
        keep_separator=True,
    )


def chunk_text(
    text: str,
    source: str,
    chunk_size: int = 800,
    chunk_overlap: int = 100,
) -> List[Dict[str, str]]:
    splitter = build_splitter(chunk_size, chunk_overlap)
    chunks = splitter.split_text(text)
    return [
        {"chunk_id": index + 1, "source": source, "content": chunk}
        for index, chunk in enumerate(chunks)
    ]


def chunk_extracted_payload(
    payload: Dict,
    source: str,
    chunk_size: int = 800,
    chunk_overlap: int = 100,
) -> Tuple[List[Dict[str, str]], Dict[str, int]]:
    text = payload.get("extracted_text", "")
    chunks = chunk_text(text, source, chunk_size, chunk_overlap)
    metadata = {
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "chunk_count": len(chunks),
    }
    return chunks, metadata


def chunk_and_save(
    extracted_file: Path,
    chunk_size: int = 800,
    chunk_overlap: int = 100,
) -> Path:
    payload = extracted_file.read_text(encoding="utf-8")
    data = __import__("json").loads(payload)
    source = data.get("filename", extracted_file.stem)
    chunks, metadata = chunk_extracted_payload(
        data,
        source=source,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    output = {
        "source": source,
        "chunks": chunks,
        "metadata": metadata,
    }
    return save_chunks_json(extracted_file.name, output)
