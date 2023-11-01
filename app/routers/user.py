from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


from ..repository import user as user_repository
from ..repository import authentication as authentication_repository
from ..schemas import user as user_schemas
from ..database.base import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/sign-up", response_model=user_schemas.ShowUser)
def create_user(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = user_repository.get_one_by_email(user.email, db, True)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"user {user.email} already exists",
        )
    created_user = user_repository.create(
        user,
        db,
    )
    user_repository.save_auth_code(
        created_user.id,
        "verification_code",
        authentication_repository.generate_verification_code(),
        db,
    )
    return created_user
