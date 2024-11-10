from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database.models import curation as curation_model
from ..schemas import curation as curation_schemas
from ..database.base import get_db
from datetime import datetime


def get_all(db: Session = Depends(get_db)):
    return db.query(
        curation_model.Curation,
    ).all()


def get_one(
    id: str, db: Session = Depends(get_db), ignore_not_found_exception: bool = False
):
    curation = db.query(curation_model.Curation).filter(curation_model.Curation.id == id).first()
    if not curation and not ignore_not_found_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"curation {id} not available"
        )
    return curation

def get_one_by_title(
    title: str, db: Session = Depends(get_db), ignore_not_found_exception: bool = False
):
    curation = db.query(curation_model.Curation).filter(curation_model.Curation.title == title).first()
    if not curation and not ignore_not_found_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"curation {id} not available"
        )
    return curation


def create(req_body: curation_schemas.CreateCuration, db: Session = Depends(get_db)):
    new_curation = curation_model.Curation(
        title=req_body.title,
        description=req_body.description,
    )
    db.add(new_curation)
    db.commit()
    db.refresh(new_curation)
    return new_curation


def update(id, update_data: dict, db: Session = Depends(get_db)):
    curation = db.query(curation_model.Curation).get(id)
    if not curation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"curation {id} not available"
        )

    for key, value in update_data.items():
        if hasattr(curation, key):
            if (value is None) and (not curation_model.Curation.__table__.c[key].nullable):
                continue
            setattr(curation, key, value)
    setattr(curation, "updated_at", datetime.utcnow())
    db.commit()