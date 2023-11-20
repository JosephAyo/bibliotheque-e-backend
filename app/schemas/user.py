from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

from .role import Role


class NoExtraBaseModel(BaseModel):
    class Config:
        extra = "forbid"


class User(NoExtraBaseModel):
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    is_email_verified: bool
    is_verified: bool
    is_deactivated: bool


class ShowUser(NoExtraBaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    is_email_verified: bool
    is_verified: bool


class AdminShowUser(ShowUser):
    created_at: datetime
    updated_at: datetime


class UserSignUp(NoExtraBaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class UserVerifyEmail(NoExtraBaseModel):
    email: EmailStr
    verification_code: str


class UserResendVerificationEmail(NoExtraBaseModel):
    email: EmailStr


class UserLoginCredentials(NoExtraBaseModel):
    email: EmailStr
    password: str


class UserLoginResponse(NoExtraBaseModel):
    access_token: str
    user: ShowUser


class TokenData(NoExtraBaseModel):
    email: Optional[str] = None


class UserForgotPassword(NoExtraBaseModel):
    email: EmailStr


class UserResetPassword(NoExtraBaseModel):
    email: EmailStr
    password: str
    code: str


class UserChangePassword(NoExtraBaseModel):
    current_password: str
    new_password: str


class CreateUserRoleAssociation(NoExtraBaseModel):
    user_id: str
    role_id: str


class ShowUserRoleAssociation(CreateUserRoleAssociation):
    id: str
    user_id: str
    role_id: str
    created_at: datetime
    updated_at: datetime
    role: Role


class UserViewProfileData(ShowUser):
    user_role_associations: List[ShowUserRoleAssociation] = []


class AdminUserViewProfileData(AdminShowUser):
    user_role_associations: List[ShowUserRoleAssociation] = []


class UserViewProfile(NoExtraBaseModel):
    message: str
    data: UserViewProfileData


class UserEditProfile(NoExtraBaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class AddManagerUser(NoExtraBaseModel):
    email: str
    role_id: str


class ViewAllUsers(NoExtraBaseModel):
    message: str
    data: List[AdminUserViewProfileData] = []
