from typing import Optional
from pydantic import BaseModel
from src.documents import ResourceID
from src.schemas.question import Question


class Poll(BaseModel):
    id: Optional[ResourceID]
    name: Optional[str]
    description: Optional[str]
    published: Optional[bool]
    questions: Optional[list[Question]]

    class Config:
        schema_extra = {
            "example": {
                "id": "1a2b3c4d5e6f7g8h9i0j",
                "name": "Poll 01",
                "description": "This is an example poll",
                "published": True
            }
        }