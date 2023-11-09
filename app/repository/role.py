from fastapi import Depends, HTTPException, status

from ..database.base import get_db
from ..schemas import role as role_schemas
from ..database.models import role as role_models
from ..database.models import (
    role_permission_association as role_permission_association_models,
)
from datetime import datetime
from sqlalchemy.orm import Session


def get_all(db: Session = Depends(get_db)):
    roles = db.query(role_models.Role).all()
    return roles


def get_one_by_name(
    name, db: Session = Depends(get_db), ignore_not_found_exception: bool = False
):
    role = db.query(role_models.Role).filter(role_models.Role.name == name).first()
    if not role and not ignore_not_found_exception:
        # response.status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"role {name} not available"
        )
    return role


def create(req_body: role_schemas.CreateRole, db: Session = Depends(get_db)):
    new_role = role_models.Role(
        name=req_body.name,
        description=req_body.description,
    )
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role


def update(id, update_data: dict, db: Session = Depends(get_db)):
    role = db.query(role_models.Role).get(id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"role {id} not available"
        )

    for key, value in update_data.items():
        if hasattr(role, key):
            if (value is None) and (not role_models.Role.__table__.c[key].nullable):
                continue
            setattr(role, key, value)
    setattr(role, "updated_at", datetime.utcnow())
    db.commit()


def destroy(id, db: Session = Depends(get_db)):
    role = db.query(role_models.Role).filter(role_models.Role.id == id)
    if not role.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"role {id} not available"
        )
    role.delete(synchronize_session=False)
    db.commit()


def create_role_permission_association(
    data: role_schemas.CreateRolePermissionAssociation, db: Session = Depends(get_db)
):
    new_role_permission_association = (
        role_permission_association_models.RolePermissionAssociation(
            role_id=data.role_id, permission_id=data.permission_id
        )
    )
    db.add(new_role_permission_association)
    db.commit()
    db.refresh(new_role_permission_association)
    return new_role_permission_association
