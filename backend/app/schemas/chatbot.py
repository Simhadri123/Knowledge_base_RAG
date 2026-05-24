from typing import List, Optional

from pydantic import BaseModel, Field


class ChatbotQueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)
    min_score: float = Field(default=0.2, ge=0.0, le=1.0)
    model: str = Field(default="openai/gpt-oss-120b:free")


class ChatbotChunk(BaseModel):
    kb_id: str
    title: str
    owner_username: str
    section: str
    content: str
    score: float


class ChatbotQueryResponse(BaseModel):
    session_id: Optional[str] = None
    query: str
    answer: str
    retrieved: List[ChatbotChunk]
    used_context: bool
    debug_prompt: Optional[str] = None
