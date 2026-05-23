from typing import Dict, Optional

from pydantic import BaseModel


class ExtractionResponse(BaseModel):
    filename: str
    stored_path: str
    extracted_path: str
    file_type: str
    text: str
    metadata: Optional[Dict[str, str]] = None
