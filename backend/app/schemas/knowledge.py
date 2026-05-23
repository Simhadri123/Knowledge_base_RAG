from typing import List, Optional

from pydantic import BaseModel, Field


class KnowledgeFromTextRequest(BaseModel):
    source: str = Field(default="document")
    text: str
    chunk_size: int = Field(default=1200, ge=200, le=8000)
    chunk_overlap: int = Field(default=150, ge=0, le=2000)
    max_parts: int = Field(default=10, ge=1, le=20)
    save_output: bool = True


class KnowledgeFromExtractedRequest(BaseModel):
    extracted_filename: str
    chunk_size: int = Field(default=1200, ge=200, le=8000)
    chunk_overlap: int = Field(default=150, ge=0, le=2000)
    max_parts: int = Field(default=10, ge=1, le=20)
    save_output: bool = True


class KnowledgeResponse(BaseModel):
    source: str
    title: str
    content: str
    raw_response: str
    chunk_count: int
    step_outputs: Optional[List[str]] = None


class KnowledgeApproveRequest(BaseModel):
    source: str = Field(default="document")
    title: str
    content: str


class KnowledgeApproveResponse(BaseModel):
    source: str
    saved_path: str


class KnowledgeAssetResponse(BaseModel):
    asset_path: str
    saved_path: str
