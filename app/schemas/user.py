from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    is_email_verified: bool
    is_verified: bool
    is_deactivated: bool


class ShowUser(BaseModel):
    first_name: str
    last_name: str
    email: str
    is_email_verified: bool
    is_verified: bool
    is_deactivated: bool


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str


class UserUpdate(BaseModel):
    first_name: str
    last_name: str
    email: str


class UserVerifyEmail(BaseModel):
    email: str
    verification_code: str

class UserResendVerificationEmail(BaseModel):
    email: str

class Login(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    user: ShowUser


class TokenData(BaseModel):
    email: Optional[str] = None
