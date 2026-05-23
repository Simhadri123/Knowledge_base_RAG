from pathlib import Path
from typing import Dict, Tuple

import fitz


def extract_pdf_text(file_path: Path) -> Tuple[str, Dict[str, str]]:
    doc = fitz.open(str(file_path))
    pages = []
    for page in doc:
        text = page.get_text().strip()
        if text:
            pages.append(text)
    combined = "\n".join(pages).strip()
    return combined, {"pages": str(doc.page_count)}
