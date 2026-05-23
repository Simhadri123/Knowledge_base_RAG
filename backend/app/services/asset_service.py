from pathlib import Path
from typing import Dict

from fastapi import UploadFile

from ..storage import save_knowledge_asset

ALLOWED_ASSET_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def save_image_asset(file: UploadFile) -> Dict:
    if not file.filename:
        raise ValueError("Missing filename")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_ASSET_EXTENSIONS:
        raise ValueError("Unsupported asset type")

    data = file.file.read()
    if not data:
        raise ValueError("Empty file")

    saved_path = save_knowledge_asset(file.filename, data)
    return {
        "asset_path": f"assets/{saved_path.name}",
        "saved_path": str(saved_path),
    }
