from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = BASE_DIR / "uploads"
EXTRACTED_DIR = BASE_DIR / "extracted"
CHUNKS_DIR = BASE_DIR / "chunks"
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
KNOWLEDGE_ASSETS_DIR = KNOWLEDGE_BASE_DIR / "assets"
ALLOWED_EXTENSIONS = {".txt", ".vtt", ".docx", ".pptx", ".pdf", ".png", ".jpg", ".jpeg"}
