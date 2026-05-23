from pathlib import Path
from typing import Dict, Tuple

from .config import ALLOWED_EXTENSIONS
from .extractors.docx import extract_docx_text
from .extractors.image import extract_image_text
from .extractors.pdf import extract_pdf_text
from .extractors.pptx import extract_pptx_text
from .extractors.vtt import extract_vtt_text


def extract_text(file_path: Path) -> Tuple[str, Dict[str, str]]:
    extension = file_path.suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {extension}")
    if extension == ".vtt":
        return extract_vtt_text(file_path)
    if extension == ".docx":
        return extract_docx_text(file_path)
    if extension == ".pptx":
        return extract_pptx_text(file_path)
    if extension == ".pdf":
        return extract_pdf_text(file_path)
    return extract_image_text(file_path)
