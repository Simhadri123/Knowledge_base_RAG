from datetime import datetime
from pathlib import Path
from typing import List

from sqlalchemy.orm import Session, joinedload

from ..models import KBArticle
from .vector_store_service import sync_vector_store


def create_kb(db: Session, owner_id: int, title: str, content_md: str, source_document: str | None = None, source_document_url: str | None = None) -> KBArticle:
    now = datetime.utcnow()
    kb = KBArticle(
        owner_id=owner_id,
        title=title,
        source_document=source_document,
        source_document_url=source_document_url,
        content_md=content_md,
        created_at=now,
        updated_at=now,
        is_published=False,
    )
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return kb


def update_kb(db: Session, kb: KBArticle, title: str | None, content_md: str | None, source_document: str | None = None, source_document_url: str | None = None) -> KBArticle:
    if title is not None:
        kb.title = title
    if content_md is not None:
        kb.content_md = content_md
    if source_document is not None:
        kb.source_document = source_document
    if source_document_url is not None:
        kb.source_document_url = source_document_url
    kb.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(kb)
    if kb.is_published:
        base_dir = Path(__file__).resolve().parents[2]
        sync_vector_store(db, base_dir / "vector_store")
    return kb


def delete_kb(db: Session, kb: KBArticle) -> None:
    was_published = kb.is_published
    db.delete(kb)
    db.commit()
    if was_published:
        base_dir = Path(__file__).resolve().parents[2]
        sync_vector_store(db, base_dir / "vector_store")


def publish_kb(db: Session, kb: KBArticle, publish: bool) -> KBArticle:
    kb.is_published = publish
    kb.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(kb)

    base_dir = Path(__file__).resolve().parents[2]
    sync_vector_store(db, base_dir / "vector_store")
    return kb


def list_user_kbs(db: Session, owner_id: int) -> List[KBArticle]:
    return (
        db.query(KBArticle)
        .filter(KBArticle.owner_id == owner_id)
        .order_by(KBArticle.updated_at.desc())
        .all()
    )


def list_published_kbs(db: Session) -> List[KBArticle]:
    return (
        db.query(KBArticle)
        .options(joinedload(KBArticle.owner))
        .filter(KBArticle.is_published == True)
        .order_by(KBArticle.updated_at.desc())
        .all()
    )


def get_kb(db: Session, kb_id: int) -> KBArticle | None:
    return db.query(KBArticle).filter(KBArticle.id == kb_id).first()
