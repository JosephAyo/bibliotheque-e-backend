from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.helpers.date_time import convert_db_timestamp_to_datetime
from app.repository.hashing import create_hash, verify_hash


from ..repository import user as user_repository
from ..repository import authentication as authentication_repository
from ..schemas import user as user_schemas
from ..database.base import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/sign-up", response_model=user_schemas.UserResponse)
def create_user(req_body: user_schemas.UserSignUp, db: Session = Depends(get_db)):
    db_user = user_repository.get_one_by_email(req_body.email, db, True)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"user {req_body.email} already exists",
        )
    created_user = user_repository.create(
        req_body,
        db,
    )
    verification_code = authentication_repository.generate_auth_code()
    user_repository.save_auth_code(
        created_user.id,
        "verification_code",
        verification_code,
        db,
    )
    # send verification code to email
    return created_user


@router.post("/verify-email")
def verify_email(req_body: user_schemas.UserVerifyEmail, db: Session = Depends(get_db)):
    existing_user = user_repository.get_one_by_email(req_body.email, db)
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
        req_body.verification_code,
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
    update_data = {"is_verified": True, "is_email_verified": True}
    user_repository.update(existing_user.id, update_data, db)
    return {"message": "success", "detail": "email verified"}


@router.post("/resend-verification/email")
def resend_verification_email(
    req_body: user_schemas.UserResendVerificationEmail, db: Session = Depends(get_db)
):
    existing_user = user_repository.get_one_by_email(req_body.email, db)
    verification_code = authentication_repository.generate_auth_code()
    user_repository.save_auth_code(
        existing_user.id,
        "verification_code",
        verification_code,
        db,
    )
    # send verification code to email
    return {"message": "success", "detail": "verification email sent"}


@router.post(
    "/login",
    response_model=user_schemas.UserLoginResponse,
)
def login(
    req_body: user_schemas.UserLoginCredentials,
    db: Session = Depends(get_db),
):
    user = user_repository.get_one_by_email(req_body.email, db)
    if not verify_hash(
        req_body.password,
        user.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"incorrect credentials"
        )
    access_token = authentication_repository.create_access_token(
        data={"email": user.email}
    )
    return {"access_token": access_token, "user": user}


@router.post("/forgot-password")
def forgot_password(
    req_body: user_schemas.UserForgotPassword, db: Session = Depends(get_db)
):
    existing_user = user_repository.get_one_by_email(req_body.email, db)
    reset_password_code = authentication_repository.generate_auth_code()
    user_repository.save_auth_code(
        existing_user.id,
        "reset_password_code",
        reset_password_code,
        db,
    )
    # send verification code to email
    return {"message": "success", "detail": "reset password code sent"}


@router.post("/reset-password")
def reset_password(
    req_body: user_schemas.UserResetPassword, db: Session = Depends(get_db)
):
    existing_user = user_repository.get_one_by_email(req_body.email, db)
    if not (
        existing_user.reset_password_code
        and existing_user.reset_password_code_last_generated_at
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"invalid reset password code",
        )
    total_seconds = (
        (convert_db_timestamp_to_datetime(db.query(func.now())))
        - existing_user.reset_password_code_last_generated_at
    ).total_seconds()

    if total_seconds > (5 * 60):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"expired reset password code",
        )

    if not verify_hash(
        req_body.code,
        existing_user.reset_password_code,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"incorrect reset password code"
        )
    user_repository.invalidate_auth_code(
        existing_user.id,
        "reset_password_code",
        db,
    )
    update_data = {
        "password": create_hash(req_body.password),
    }
    user_repository.update(existing_user.id, update_data, db)
    return {"message": "success", "detail": "password reset"}
