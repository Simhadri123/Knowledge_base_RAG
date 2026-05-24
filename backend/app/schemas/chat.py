from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ChatHistoryResponse(BaseModel):
    id: int
    user_id: int
    session_id: Optional[str] = None
    query: str
    answer: str
    created_at: datetime

    class Config:
        orm_mode = True
