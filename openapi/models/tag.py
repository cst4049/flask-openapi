from typing import Optional
from pydantic import BaseModel


class Tag(BaseModel):
    name: str
    description: Optional[str] = None
