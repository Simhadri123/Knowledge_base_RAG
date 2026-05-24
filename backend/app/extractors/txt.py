from pathlib import Path
from typing import Dict, Tuple


def extract_txt_text(file_path: Path) -> Tuple[str, Dict[str, str]]:
    text = file_path.read_text(encoding="utf-8", errors="replace").strip()
    return text, {"length": str(len(text))}
