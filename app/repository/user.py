from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status

from ..database.base import get_db
from ..schemas import user as user_schemas
from ..database.models import user as user_models
from ..database.models import user_role_association as user_role_association_models

from sqlalchemy.orm import Session
from .hashing import create_hash


def get_all(db: Session = Depends(get_db)):
    users = db.query(user_models.User).all()
    return users


def get_one(
    id, db: Session = Depends(get_db), ignore_not_found_exception: bool = False
):
    user = db.query(user_models.User).filter(user_models.User.id == id).first()
    if not user and not ignore_not_found_exception:
        # response.status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"user {id} not available"
        )
    return user


def get_one_by_email(
    email, db: Session = Depends(get_db), ignore_not_found_exception: bool = False
):
    user = db.query(user_models.User).filter(user_models.User.email == email).first()
    if not user and not ignore_not_found_exception:
        # response.status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"user {email} not available"
        )
    return user


def create(req_body: user_schemas.UserSignUp, db: Session = Depends(get_db)):
    new_user = user_models.User(
        first_name=req_body.first_name,
        last_name=req_body.last_name,
        email=req_body.email,
        password=create_hash(req_body.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update(id, update_data: dict, db: Session = Depends(get_db)):
    user = db.query(user_models.User).get(id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"user {id} not available"
        )

    for key, value in update_data.items():
        if hasattr(user, key):
            if (value is None) and (not user_models.User.__table__.c[key].nullable):
                continue
            setattr(user, key, value)
    setattr(user, "updated_at", datetime.utcnow())
    db.commit()


def destroy(id, db: Session = Depends(get_db)):
    user = db.query(user_models.User).filter(user_models.User.id == id)
    if not user.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"user {id} not available"
        )
    user.delete(synchronize_session=False)
    db.commit()


def save_auth_code(
    id: str, code_col_name: str, code: str, db: Session = Depends(get_db)
):
    user = db.query(user_models.User).get(id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"user {id} not available"
        )
    setattr(user, code_col_name, create_hash(code))
    setattr(user, code_col_name + "_last_generated_at", datetime.utcnow())
    setattr(user, "updated_at", datetime.utcnow())
    db.commit()


def invalidate_auth_code(id: str, code_col_name: str, db: Session = Depends(get_db)):
    user = db.query(user_models.User).get(id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"user {id} not available"
        )
    setattr(user, code_col_name, None)
    setattr(
        user,
        code_col_name + "_last_generated_at",
        (
            getattr(user, code_col_name + "_last_generated_at", datetime.utcnow())
            - timedelta(days=40)
        ),
    )
    setattr(user, "updated_at", datetime.utcnow())
    db.commit()


def get_user_role_association(
    id: str, db: Session = Depends(get_db), ignore_not_found_exception=False
):
    user_role_association = db.query(
        user_role_association_models.UserRoleAssociation
    ).get(id)
    if not user_role_association and not ignore_not_found_exception:
        # response.status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user role association {id} not available",
        )

    return user_role_association


def create_user_role_association(
    data: user_schemas.CreateUserRoleAssociation, db: Session = Depends(get_db)
):
    new_user_role_association = user_role_association_models.UserRoleAssociation(
        user_id=data.user_id,
        role_id=data.role_id,
    )
    db.add(new_user_role_association)
    db.commit()
    db.refresh(new_user_role_association)
    return new_user_role_association
