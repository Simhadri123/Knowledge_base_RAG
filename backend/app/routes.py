from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

from .config import ALLOWED_EXTENSIONS
from .extraction import extract_text
from .schemas import ExtractionResponse
from .storage import save_extraction_json, save_upload_file

router = APIRouter()


@router.post("/upload", response_model=ExtractionResponse)
async def upload_file(file: UploadFile) -> ExtractionResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")
    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {extension}")

    try:
        stored_path = save_upload_file(file)
        text, metadata = extract_text(stored_path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    payload = {
        "filename": file.filename,
        "stored_path": str(stored_path),
        "file_type": extension,
        "extracted_text": text,
        "metadata": metadata,
        "extracted_at": datetime.utcnow().isoformat() + "Z",
    }
    extracted_path = save_extraction_json(stored_path.name, payload)

    return ExtractionResponse(
        filename=file.filename,
        stored_path=str(stored_path),
        extracted_path=str(extracted_path),
        file_type=extension,
        text=text,
        metadata=metadata,
    )
