from typing import List, Optional

from pydantic import BaseModel, Field


class ChunkFromTextRequest(BaseModel):
    source: str = Field(default="document")
    text: str
    chunk_size: int = Field(default=800, ge=100, le=5000)
    chunk_overlap: int = Field(default=100, ge=0, le=2000)
    save: bool = True


class ChunkFromExtractedRequest(BaseModel):
    extracted_filename: str
    chunk_size: int = Field(default=800, ge=100, le=5000)
    chunk_overlap: int = Field(default=100, ge=0, le=2000)
    save: bool = True


class ChunkItem(BaseModel):
    chunk_id: int
    source: str
    content: str


class ChunkMetadata(BaseModel):
    chunk_size: int
    chunk_overlap: int
    chunk_count: int


class ChunkResponse(BaseModel):
    source: str
    chunks: List[ChunkItem]
    metadata: ChunkMetadata
    saved_path: Optional[str] = None
