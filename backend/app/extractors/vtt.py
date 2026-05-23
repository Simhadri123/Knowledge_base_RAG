import re
from pathlib import Path
from typing import Dict, Tuple


TIMESTAMP_PATTERN = re.compile(r"^\d{2}:\d{2}:\d{2}\.\d{3}\s+-->\s+\d{2}:\d{2}:\d{2}\.\d{3}")


def extract_vtt_text(file_path: Path) -> Tuple[str, Dict[str, str]]:
    lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.upper() == "WEBVTT":
            continue
        if TIMESTAMP_PATTERN.match(stripped):
            continue
        if stripped.isdigit():
            continue
        cleaned.append(stripped)
    text = " ".join(cleaned).strip()
    return text, {"lines": str(len(cleaned))}
