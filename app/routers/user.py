from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.helpers.date_time import convert_db_timestamp_to_datetime
from app.repository.hashing import verify_hash


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


@router.post("/verify-email")
def verify_email(user: user_schemas.UserVerifyEmail, db: Session = Depends(get_db)):
    existing_user = user_repository.get_one_by_email(user.email, db)
    if not (
        existing_user.verification_code
        and existing_user.verification_code_last_generated_at
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"invalid verification code",
        )
    total_seconds = (
        (convert_db_timestamp_to_datetime(db.query(func.now())))
        - existing_user.verification_code_last_generated_at
    ).total_seconds()

    if total_seconds > (5 * 60):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"expired verification code",
        )

    if not verify_hash(
        user.verification_code,
        existing_user.verification_code,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"incorrect verification code"
        )
    user_repository.invalidate_auth_code(
        existing_user.id,
        "verification_code",
        db,
    )
    return {"message": "success", "detail": "email verified"}


@router.post("/resend-verification/email")
def resend_verification_email(
    user: user_schemas.UserResendVerificationEmail, db: Session = Depends(get_db)
):
    existing_user = user_repository.get_one_by_email(user.email, db)
    user_repository.save_auth_code(
        existing_user.id,
        "verification_code",
        authentication_repository.generate_verification_code(),
        db,
    )
    return {"message": "success", "detail": "verification email sent"}
