from pathlib import Path
from typing import Dict, Tuple
import os
import shutil

from PIL import Image
import pytesseract


def _configure_tesseract() -> None:
    env_cmd = os.getenv("TESSERACT_CMD")
    if env_cmd and Path(env_cmd).exists():
        pytesseract.pytesseract.tesseract_cmd = env_cmd
        return

    if shutil.which("tesseract"):
        return

    default_path = Path("C:/Program Files/Tesseract-OCR/tesseract.exe")
    if default_path.exists():
        pytesseract.pytesseract.tesseract_cmd = str(default_path)


def extract_image_text(file_path: Path) -> Tuple[str, Dict[str, str]]:
    _configure_tesseract()
    image = Image.open(str(file_path))
    text = pytesseract.image_to_string(image).strip()
    return text, {"width": str(image.width), "height": str(image.height)}
