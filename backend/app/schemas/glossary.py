from typing import Optional, List
from pydantic import BaseModel, Field

class GlossaryItem(BaseModel):
    id: Optional[int] = None
    term: str = Field(..., description="Term to match")
    action: str = Field(default="preserve", description="'preserve' or 'preferred'")
    replacement: Optional[str] = Field(None, description="Preferred translation if action is 'preferred'")
    target_language: Optional[str] = Field(None, description="Applies to specific target language, or all if null")

class GlossaryCreate(BaseModel):
    term: str
    action: str = "preserve"
    replacement: Optional[str] = None
    target_language: Optional[str] = None

class GlossaryResponse(BaseModel):
    items: List[GlossaryItem]
    total: int
