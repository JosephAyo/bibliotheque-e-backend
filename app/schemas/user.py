from typing import Optional
from pydantic import BaseModel, EmailStr


class User(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    is_email_verified: bool
    is_verified: bool
    is_deactivated: bool


class ShowUser(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    is_email_verified: bool
    is_verified: bool
    is_deactivated: bool


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class UserVerifyEmail(BaseModel):
    email: EmailStr
    verification_code: str

class UserResendVerificationEmail(BaseModel):
    email: EmailStr

class Login(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    user: ShowUser


class TokenData(BaseModel):
    email: Optional[str] = None
