from beanie import PydanticObjectId
from pydantic import BaseModel, Field, EmailStr
from typing import List
# from random import choice, randint
from fastapi import Response
# from app.models.group import Group
# from app.models.user import User
from app.schemas.user import UserAddToGroup


class GroupID(PydanticObjectId):
    @classmethod
    def __modify_schema__(cls, field_schema):  # type: ignore
        field_schema.update(
            type="string",
            example="5eb7cf5a86d9755df3a6c593",
        )


class GroupReadSimple(BaseModel):
    name: str = Field(title="Name")
    role: str = Field(title="Role")

    class Config:
        schema_extra = {
            "example": {
                "name": "Group 01",
                "role": "user",
            }
        }


class GroupReadFull(BaseModel):
    name: str = Field(example="Group 01", title="Name")
    description: str
    owner_name: str
    owner_email: EmailStr
    # TODO: Add list of members (emails with roles)

    class Config:
        schema_extra = {
            "example": {
                "name": "Example Group",
                "description": "This is an example group",
                "owner_name": "John Doe",
                "owner_email": "jdoe@example.com",
            }
        }


class GroupList(BaseModel):
    groups: List[GroupReadSimple]

    class Config:
        schema_extra = {
            "example": {
                "groups": [
                    {"name": "Group 01", "role": "user"},
                    {"name": "Group 02", "role": "user"},
                    {"name": "Group 03", "role": "admin"},
                ]
            }
        }


class GroupCreateIn(BaseModel):
    name: str = Field(
        default="",
        min_length=3,
        max_length=50,
        regex="^[A-Z][A-Za-z]{2,}([ ]([0-9]+|[A-Z][A-Za-z]*))*$")
    description: str = Field(default="", title="Description", max_length=300)

    class Config:
        schema_extra = {
            "example": {
                "name": "Group 01",
                "description": "My first Group",
            }
        }


class GroupCreateOut(BaseModel):
    message: str = "Group created successfully"
    id: GroupID
    name: str
    # description: str


class GroupUpdateIn(BaseModel):
    name: str = Field(
        default="",
        min_length=3,
        max_length=50,
        regex="^[A-Z][A-Za-z]{2,}([ ]([0-9]+|[A-Z][A-Za-z]*))*$")
    description: str = Field(default="", title="Description", max_length=300)


class GroupUpdateOut(Response):
    status_code = 200
    media_type = "application/json"
    content = {"message": "Group updated successfully"}


class GroupMember(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: str = Field(default="user", title="Role")

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "role": "user",
            }
        }


class GroupAddMembers(BaseModel):
    members: List[UserAddToGroup]

    class Config:
        schema_extra = {
            "example": {
                "members": [
                    {"email": "user1@example.com", "role": "admin"},
                    {"email": "user2@example.com", "role": "user"},
                ]
            }
        }


class GroupReadMembers(BaseModel):
    members: List[GroupMember]

    class Config:
        schema_extra = {
            "example": {
                "members": [
                    {
                        "email": "jdoe@example.com",
                        "first_name": "John",
                        "last_name": "Doe",
                        "role": "admin"
                    },
                    {
                        "email": "jsmith@example.com",
                        "first_name": "Jack",
                        "last_name": "Smith",
                        "role": "user"
                    }
                ]
            }
        }


class GroupMemberUpdateRole(BaseModel):
    role: str = Field(example="admin", title="Role")
