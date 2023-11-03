from typing import Optional
from pydantic import BaseModel, EmailStr


class NoExtraBaseModel(BaseModel):
    class Config:
        extra = "forbid"


class User(NoExtraBaseModel):
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
    email: EmailStr
    current_password: str
    new_password: str


class UserViewProfile(NoExtraBaseModel):
    message: str
    data: ShowUser
