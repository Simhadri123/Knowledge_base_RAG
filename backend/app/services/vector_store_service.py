import logging
from datetime import datetime
from pathlib import Path
from typing import List

from sqlalchemy.orm import Session

from ..models import KBArticle, KBEmbeddingMetadata, User
from ..rag.chunking import split_markdown
from ..rag.embedding import LocalEmbedder
from ..rag.indexing import build_index

logger = logging.getLogger("vector.sync")


def sync_vector_store(db: Session, vector_dir: Path) -> int:
    vector_dir = Path(vector_dir)
    vector_dir.mkdir(parents=True, exist_ok=True)

    published = (
        db.query(KBArticle)
        .join(User, KBArticle.owner_id == User.id)
        .filter(KBArticle.is_published.is_(True))
        .all()
    )

    if not published:
        db.query(KBEmbeddingMetadata).delete()
        db.commit()
        index_path = vector_dir / "kb.index.faiss"
        meta_path = vector_dir / "kb.metadata.json"
        if index_path.exists():
            index_path.unlink()
        if meta_path.exists():
            meta_path.unlink()
        logger.info("No published KBs. Cleared vector store.")
        return 0

    chunks: List[dict] = []
    for article in published:
        owner_name = article.owner.username if article.owner else "unknown"
        for chunk in split_markdown(str(article.id), article.title, article.content_md):
            chunks.append(
                {
                    "kb_id": str(article.id),
                    "title": article.title,
                    "section": chunk.section,
                    "content": chunk.content,
                    "owner_username": owner_name,
                }
            )

    embedder = LocalEmbedder()
    build_index(chunks, embedder, vector_dir)

    db.query(KBEmbeddingMetadata).delete()
    for idx, chunk in enumerate(chunks):
        db.add(
            KBEmbeddingMetadata(
                kb_id=int(chunk["kb_id"]),
                vector_index=idx,
                title=chunk["title"],
                section=chunk["section"],
                content=chunk["content"],
                owner_username=chunk["owner_username"],
                created_at=datetime.utcnow(),
            )
        )
    db.commit()

    logger.info("Vector store synced with %s chunks", len(chunks))
    return len(chunks)
