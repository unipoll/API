from typing import List
from beanie import PydanticObjectId
from fastapi_users.db import BeanieBaseUser
from pydantic import Field


class User(BeanieBaseUser[PydanticObjectId]):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    # groups: Dict[List[PydanticObjectId], str] = {}
    groups: List[PydanticObjectId] = []
    first_name: str = Field(
        default_factory=str,
        max_length=20,
        min_length=2,
        regex="^[A-Z][a-z]*$")
    last_name: str = Field(
        default_factory=str,
        max_length=20,
        min_length=2,
        regex="^[A-Z][a-z]*$")
