from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database.enums import UserRole
from ..helpers.email_templates import get_reset_password_email, get_verification_email
from ..helpers.send_email import send_email_background

from ..repository.hashing import create_hash, verify_hash


from ..repository import user as user_repository
from ..repository import authentication as authentication_repository
from ..schemas import user as user_schemas
from ..schemas import generic as generic_schemas
from ..schemas import role as role_schemas
from ..database.base import get_db
from ..repository import role as role_repository

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/sign-up",
    response_model=user_schemas.ShowUser,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    req_body: user_schemas.UserSignUp,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
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
    user_role = role_repository.get_one_by_name(UserRole.BORROWER.value, db, True)
    if user_role is not None:
        user_repository.create_user_role_association(
            user_schemas.CreateUserRoleAssociation(
                **{"user_id": created_user.id, "role_id": user_role.id}
            ),
            db,
        )
    verification_code = authentication_repository.generate_auth_code()
    user_repository.save_auth_code(
        created_user.id,
        "verification_code",
        verification_code,
        db,
    )
    send_email_background(
        background_tasks,
        "Welcome",
        f"{req_body.email}",
        get_verification_email(created_user.first_name, verification_code),
    )
    return created_user


@router.patch("/verify-email", response_model=generic_schemas.NoDataResponse)
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
        datetime.utcnow() - existing_user.verification_code_last_generated_at
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


@router.post(
    "/resend-verification/email", response_model=generic_schemas.NoDataResponse
)
def resend_verification_email(
    req_body: user_schemas.UserResendVerificationEmail,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    existing_user = user_repository.get_one_by_email(req_body.email, db)
    verification_code = authentication_repository.generate_auth_code()
    user_repository.save_auth_code(
        existing_user.id,
        "verification_code",
        verification_code,
        db,
    )

    send_email_background(
        background_tasks,
        "Email verification",
        f"{req_body.email}",
        get_verification_email(existing_user.first_name, verification_code),
    )
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
    access_token = authentication_repository.create_access_token(data={"id": user.id})
    return {"access_token": access_token, "user": user}


@router.patch("/forgot-password", response_model=generic_schemas.NoDataResponse)
def forgot_password(
    req_body: user_schemas.UserForgotPassword,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    existing_user = user_repository.get_one_by_email(req_body.email, db)
    reset_password_code = authentication_repository.generate_auth_code()
    user_repository.save_auth_code(
        existing_user.id,
        "reset_password_code",
        reset_password_code,
        db,
    )

    send_email_background(
        background_tasks,
        "Reset password",
        f"{req_body.email}",
        get_reset_password_email(existing_user.first_name, reset_password_code),
    )
    return {"message": "success", "detail": "reset password code sent"}


@router.patch("/reset-password", response_model=generic_schemas.NoDataResponse)
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
        datetime.utcnow() - existing_user.reset_password_code_last_generated_at
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
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"incorrect reset password code",
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


@router.patch("/change-password", response_model=generic_schemas.NoDataResponse)
def change_password(
    req_body: user_schemas.UserChangePassword,
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_user),
):
    if not verify_hash(
        req_body.current_password,
        current_user.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"incorrect password"
        )
    if verify_hash(
        req_body.new_password,
        current_user.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"new password cannot be same as old password",
        )
    update_data = {
        "password": create_hash(req_body.new_password),
    }
    user_repository.update(current_user.id, update_data, db)
    return {"message": "success", "detail": "password changed"}


@router.get(
    "/profile",
    response_model=user_schemas.UserViewProfile,
    status_code=status.HTTP_200_OK,
)
def view_profile(
    current_user=Depends(authentication_repository.get_current_user),
):
    return {"message": "success", "data": current_user}


@router.patch("/profile", response_model=generic_schemas.NoDataResponse)
def edit_profile(
    req_body: user_schemas.UserEditProfile,
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_user),
):
    update_data = {"first_name": req_body.first_name, "last_name": req_body.last_name}
    user_repository.update(current_user.id, update_data, db)
    return {"message": "success", "detail": "profile updated"}


@router.get(
    "/roles",
    response_model=role_schemas.ViewRolesResponse,
    status_code=status.HTTP_200_OK,
)
def view_roles(
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_librarian_user),
):
    roles = role_repository.get_all_by_librarian(db)
    return {"message": "success", "data": roles}


@router.post(
    "/manager",
    response_model=generic_schemas.NoDataResponse,
    status_code=status.HTTP_201_CREATED,
)
def regulate_manager(
    req_body: user_schemas.AddOrRemoveManagerUser,
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_librarian_user),
):
    user = user_repository.get_one_by_email(req_body.email, db)
    new_association_role_ids = req_body.role_ids

    for user_role_association in user.user_role_associations:
        new_association_role_ids = list(
            filter(
                lambda role_id: role_id != user_role_association.role_id,
                new_association_role_ids,
            )
        )

        filtered_association = list(
            filter(
                lambda role_id: role_id == user_role_association.role_id
                or user_role_association.role.name == UserRole.BORROWER.value,
                req_body.role_ids,
            )
        )
        if filtered_association:
            continue
        elif not filtered_association:
            user_repository.destroy_user_role_association(
                user_role_association.id,
                db,
            )

    for role_id in new_association_role_ids:
        user = user_repository.get_one_by_email(req_body.email, db)
        user_role = role_repository.get_one_by_id(role_id, db)
        user_repository.create_user_role_association(
            user_schemas.CreateUserRoleAssociation(
                **{"user_id": user.id, "role_id": user_role.id}
            ),
            db,
        )
    return {"message": "success", "detail": "manager user updated"}


@router.get(
    "/all",
    response_model=user_schemas.ViewAllUsers,
    status_code=status.HTTP_200_OK,
)
def view_all_users(
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_librarian_user),
):
    users = user_repository.get_all(db)
    return {"message": "success", "data": users}
