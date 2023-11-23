from datetime import datetime, timedelta
import json
import os
from typing import Annotated, Any, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import random
import string
from app.database.enums import UserRole

from app.schemas.user import UserViewProfileData
from ..repository import user as user_repository
from ..database.base import SessionLocal

SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("ALGORITHM", "")
ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS", 1))

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/users/login",
)

optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login", auto_error=False)


def create_access_token(data: Union[str, Any], expires_delta: timedelta | None = None):
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(data)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data: str = payload.get("sub")
        if token_data is None:
            raise credentials_exception
        return token_data
    except JWTError:
        raise credentials_exception


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(token=token, credentials_exception=credentials_exception)
    db = SessionLocal()
    data = json.loads(token_data.replace("'", '"'))
    user = user_repository.get_one(data["id"], db, True)
    db.close()
    if user is None:
        raise credentials_exception
    return user


async def get_current_manager_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(token=token, credentials_exception=credentials_exception)
    db = SessionLocal()
    data = json.loads(token_data.replace("'", '"'))
    user: UserViewProfileData = user_repository.get_one(data["id"], db)
    db.close()
    if user is None:
        raise credentials_exception
    is_manager_user = any(
        (
            user_role_association.role.name == UserRole.PROPRIETOR.value
            or user_role_association.role.name == UserRole.LIBRARIAN.value
        )
        for user_role_association in user.user_role_associations
    )

    if not is_manager_user:
        raise credentials_exception
    return user


async def get_current_proprietor_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(token=token, credentials_exception=credentials_exception)
    db = SessionLocal()
    data = json.loads(token_data.replace("'", '"'))
    user: UserViewProfileData = user_repository.get_one(data["id"], db, True)
    db.close()
    if user is None:
        raise credentials_exception
    is_proprietor_user = any(
        (user_role_association.role.name == UserRole.PROPRIETOR.value)
        for user_role_association in user.user_role_associations
    )

    if not is_proprietor_user:
        raise credentials_exception
    return user


async def get_current_librarian_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(token=token, credentials_exception=credentials_exception)
    db = SessionLocal()
    data = json.loads(token_data.replace("'", '"'))
    user: UserViewProfileData = user_repository.get_one(data["id"], db, True)
    db.close()
    if user is None:
        raise credentials_exception
    is_librarian_user = any(
        (user_role_association.role.name == UserRole.LIBRARIAN.value)
        for user_role_association in user.user_role_associations
    )

    if not is_librarian_user:
        raise credentials_exception
    return user


async def get_current_borrower_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(token=token, credentials_exception=credentials_exception)
    db = SessionLocal()
    data = json.loads(token_data.replace("'", '"'))
    user: UserViewProfileData = user_repository.get_one(data["id"], db, True)
    db.close()
    if user is None:
        raise credentials_exception
    is_borrower_user = any(
        (user_role_association.role.name == UserRole.BORROWER.value)
        for user_role_association in user.user_role_associations
    )

    if not is_borrower_user:
        raise credentials_exception
    return user


async def get_current_user_or_none(
    token: Annotated[str, Depends(optional_oauth2_scheme)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token:
        token_data = verify_token(
            token=token, credentials_exception=credentials_exception
        )
        db = SessionLocal()
        data = json.loads(token_data.replace("'", '"'))
        user = user_repository.get_one(data["id"], db)
        db.close()
        return user
    return None


def generate_auth_code(length=6):
    # Generate a random verification code of the specified length
    characters = (
        string.digits
    )  # You can customize this to include letters or other characters
    code = "".join(random.choice(characters) for _ in range(length))
    print(f"code :>>{code}")
    return code
