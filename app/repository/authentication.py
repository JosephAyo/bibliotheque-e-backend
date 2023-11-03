from datetime import datetime, timedelta
import json
from typing import Annotated, Any, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import random
import string
from ..repository import user as user_repository
from ..database.base import SessionLocal

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "cb014ee235209cf15a7e4c1c0a0e1d6021a93420fc05f1299ee1cc56d16ca807"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/users/login",
)


def create_access_token(data: Union[str, Any], expires_delta: timedelta | None = None):
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=45)
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
    user = user_repository.get_one_by_email(data["email"], db)
    db.close()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def generate_auth_code(length=6):
    # Generate a random verification code of the specified length
    characters = (
        string.digits
    )  # You can customize this to include letters or other characters
    code = "".join(random.choice(characters) for _ in range(length))
    print(f"code :>>{code}")
    return code
