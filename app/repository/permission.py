from fastapi import Depends, HTTPException, status
from sqlalchemy import func

from ..database.base import get_db
from ..schemas import permission as permission_schemas
from ..database.models import permission as permission_models

from sqlalchemy.orm import Session


def get_all(db: Session = Depends(get_db)):
    permissions = db.query(permission_models.Permission).all()
    return permissions


def get_one_by_name(
    name, db: Session = Depends(get_db), ignore_not_found_exception: bool = False
):
    permission = db.query(permission_models.Permission).filter(permission_models.Permission.name == name).first()
    if not permission and not ignore_not_found_exception:
        # response.status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"permission {name} not available"
        )
    return permission


def create(req_body: permission_schemas.CreatePermission, db: Session = Depends(get_db)):
    new_permission = permission_models.Permission(
        name=req_body.name,
        description=req_body.description,
    )
    db.add(new_permission)
    db.commit()
    db.refresh(new_permission)
    return new_permission


def update(id, update_data: dict, db: Session = Depends(get_db)):
    permission = db.query(permission_models.Permission).get(id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"permission {id} not available"
        )

    for key, value in update_data.items():
        if hasattr(permission, key):
            if (value is None) and (not permission_models.Permission.__table__.c[key].nullable):
                continue
            setattr(permission, key, value)
    setattr(permission, "updated_at", func.now())
    db.commit()


def destroy(id, db: Session = Depends(get_db)):
    permission = db.query(permission_models.Permission).filter(permission_models.Permission.id == id)
    if not permission.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"permission {id} not available"
        )
    permission.delete(synchronize_session=False)
    db.commit()
