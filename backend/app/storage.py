import json
from pathlib import Path
from typing import Dict
from uuid import uuid4

from fastapi import UploadFile

from .config import (
    CHUNKS_DIR,
    EXTRACTED_DIR,
    KNOWLEDGE_ASSETS_DIR,
    KNOWLEDGE_BASE_DIR,
    UPLOAD_DIR,
)


def ensure_storage_dirs() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
    KNOWLEDGE_ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def save_upload_file(upload: UploadFile) -> Path:
    ensure_storage_dirs()
    suffix = Path(upload.filename).suffix
    safe_name = f"{uuid4().hex}{suffix}"
    destination = UPLOAD_DIR / safe_name
    with destination.open("wb") as buffer:
        buffer.write(upload.file.read())
    return destination


def save_extraction_json(filename: str, payload: Dict) -> Path:
    ensure_storage_dirs()
    safe_name = f"{Path(filename).stem}.json"
    destination = EXTRACTED_DIR / safe_name
    with destination.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    return destination


def save_chunks_json(filename: str, payload: Dict) -> Path:
    ensure_storage_dirs()
    safe_name = f"{Path(filename).stem}_chunks.json"
    destination = CHUNKS_DIR / safe_name
    with destination.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    return destination


def save_knowledge_json(filename: str, payload: Dict) -> Path:
    ensure_storage_dirs()
    safe_name = f"{Path(filename).stem}_knowledge.json"
    destination = KNOWLEDGE_BASE_DIR / safe_name
    with destination.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    return destination


def save_knowledge_asset(filename: str, data: bytes) -> Path:
    ensure_storage_dirs()
    suffix = Path(filename).suffix.lower()
    safe_name = f"{uuid4().hex}{suffix}"
    destination = KNOWLEDGE_ASSETS_DIR / safe_name
    with destination.open("wb") as handle:
        handle.write(data)
    return destination
