from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship, backref

from ..db.base import Base


class KBArticle(Base):
    __tablename__ = "kb_articles"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    source_document = Column(String(255), nullable=True)
    source_document_url = Column(String(1024), nullable=True)
    content_md = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_published = Column(Boolean, default=False, nullable=False)

    owner = relationship("User", backref="kb_articles")


class KBEmbeddingMetadata(Base):
    __tablename__ = "kb_embeddings_metadata"

    id = Column(Integer, primary_key=True, index=True)
    kb_id = Column(Integer, ForeignKey("kb_articles.id"), nullable=False)
    vector_index = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    section = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    owner_username = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    kb_article = relationship("KBArticle", backref=backref("embeddings", cascade="all, delete-orphan"))
