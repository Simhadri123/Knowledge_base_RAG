from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class KBCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content_md: str = Field(min_length=1)
    source_document: Optional[str] = None
    source_document_url: Optional[str] = None


class KBUpdateRequest(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)
    content_md: Optional[str] = None
    source_document: Optional[str] = None
    source_document_url: Optional[str] = None


class KBResponse(BaseModel):
    id: int
    owner_id: int
    owner_username: Optional[str] = None
    title: str
    source_document: Optional[str] = None
    source_document_url: Optional[str] = None
    content_md: str
    created_at: datetime
    updated_at: datetime
    is_published: bool


class KBListItem(BaseModel):
    id: int
    owner_username: Optional[str] = None
    title: str
    source_document: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_published: bool
