from pydantic import BaseModel
from typing import Optional

class IdeaUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
