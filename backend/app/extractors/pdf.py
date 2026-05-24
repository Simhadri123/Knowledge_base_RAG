from pathlib import Path
from typing import Dict, Tuple

import fitz
from PIL import Image
import pytesseract

from .image import _configure_tesseract


def extract_pdf_text(file_path: Path) -> Tuple[str, Dict[str, str]]:
    doc = fitz.open(str(file_path))
    pages = []
    for page in doc:
        text = page.get_text().strip()
        if text:
            pages.append(text)
    combined = "\n".join(pages).strip()

    if not combined:
        _configure_tesseract()
        for page in doc:
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = pytesseract.image_to_string(img).strip()
            if text:
                pages.append(text)
        combined = "\n".join(pages).strip()

    return combined, {"pages": str(doc.page_count)}
