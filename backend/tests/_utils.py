from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


def reset_state() -> None:
    db_path = BASE_DIR / "app.db"
    if db_path.exists():
        db_path.unlink()

    vector_dir = BASE_DIR / "vector_store"
    for file_name in ["kb.index.faiss", "kb.metadata.json"]:
        file_path = vector_dir / file_name
        if file_path.exists():
            file_path.unlink()
