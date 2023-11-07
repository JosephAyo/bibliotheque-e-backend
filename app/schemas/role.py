from datetime import datetime
from pydantic import BaseModel


class NoExtraBaseModel(BaseModel):
    class Config:
        extra = "forbid"


class CreateRole(NoExtraBaseModel):
    name: str
    description: str


class Role(CreateRole):
    id: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime


class EditRole(NoExtraBaseModel):
    id: str
    name: str
    description: str


class CreateRolePermissionAssociation(NoExtraBaseModel):
    role_id: str
    permission_id: str
