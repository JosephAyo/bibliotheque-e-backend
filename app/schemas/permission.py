from datetime import datetime
from pydantic import BaseModel


class NoExtraBaseModel(BaseModel):
    class Config:
        extra = "forbid"


class CreatePermission(NoExtraBaseModel):
    name: str
    description: str


class Permission(BaseModel):
    id: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime


class EditPermission(NoExtraBaseModel):
    id: str
    name: str
    description: str