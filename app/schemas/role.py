from datetime import datetime
from typing import List
from pydantic import BaseModel

from .permission import Permission


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


class RolePermissionAssociation(BaseModel):
    id: str
    role_id: str
    permission_id: str
    created_at: datetime
    updated_at: datetime
    permission: Permission


class ShowRoleWithPermissions(Role):
    role_permission_associations: List[RolePermissionAssociation]


class ViewRolesResponse(BaseModel):
    message: str
    data: List[ShowRoleWithPermissions]


class UserSwitchRole(NoExtraBaseModel):
    user_role_association_id: str
