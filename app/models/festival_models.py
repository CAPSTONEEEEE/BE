from pydantic import BaseModel
from typing import Optional

class Festival(BaseModel):
    id: int
    name: str
    location: str
    date: str
    description: Optional[str] = None