from pathlib import Path
from typing import Dict, Tuple

from docx import Document


def extract_docx_text(file_path: Path) -> Tuple[str, Dict[str, str]]:
    doc = Document(str(file_path))
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    text = "\n".join(paragraphs).strip()
    return text, {"paragraphs": str(len(paragraphs))}
