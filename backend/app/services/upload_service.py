from datetime import datetime
from pathlib import Path
from typing import Dict

from fastapi import UploadFile

from ..config import ALLOWED_EXTENSIONS
from ..extraction import extract_text
from ..storage import save_extraction_json, save_upload_file


def handle_upload(file: UploadFile) -> Dict:
    if not file.filename:
        raise ValueError("Missing filename")

    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {extension}")

    stored_path = save_upload_file(file)
    text, metadata = extract_text(stored_path)
    if not text.strip():
        raise ValueError("Could not extract any text from the uploaded file. Please ensure the file contains text.")

    payload = {
        "filename": file.filename,
        "stored_path": str(stored_path),
        "file_type": extension,
        "extracted_text": text,
        "metadata": metadata,
        "extracted_at": datetime.utcnow().isoformat() + "Z",
    }
    extracted_path = save_extraction_json(stored_path.name, payload)

    return {
        "filename": file.filename,
        "stored_path": str(stored_path),
        "extracted_path": str(extracted_path),
        "file_type": extension,
        "text": text,
        "metadata": metadata,
        "extracted_at": payload["extracted_at"],
    }
