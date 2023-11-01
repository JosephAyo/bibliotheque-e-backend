from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..repository import user as user_repository
from ..schemas import user as user_schemas
from ..database.base import get_db

router = APIRouter(prefix="/user", tags=["Users"])


@router.post("/signup", response_model=user_schemas.ShowUser)
def create_user(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = user_repository.get_one_by_email(user.email, db, True)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"user {user.email} already exists",
        )
    return user_repository.create(
        user,
        db,
    )
