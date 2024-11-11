from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database.models import genre as genre_model
from ..schemas import genre as genre_schemas
from ..database.base import get_db
from datetime import datetime


def count_all(db: Session = Depends(get_db)):
    return db.query(genre_model.Genre).count()


def get_all(db: Session = Depends(get_db)):
    return db.query(
        genre_model.Genre,
    ).all()


def get_one(
    id: str, db: Session = Depends(get_db), ignore_not_found_exception: bool = False
):
    genre = db.query(genre_model.Genre).filter(genre_model.Genre.id == id).first()
    if not genre and not ignore_not_found_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"genre {id} not available"
        )
    return genre

def get_one_by_name(
    name: str, db: Session = Depends(get_db), ignore_not_found_exception: bool = False
):
    genre = db.query(genre_model.Genre).filter(genre_model.Genre.name == name).first()
    if not genre and not ignore_not_found_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"genre {id} not available"
        )
    return genre


def create(req_body: genre_schemas.CreateGenre, db: Session = Depends(get_db)):
    new_genre = genre_model.Genre(
        name=req_body.name,
        description=req_body.description,
    )
    db.add(new_genre)
    db.commit()
    db.refresh(new_genre)
    return new_genre


def update(id, update_data: dict, db: Session = Depends(get_db)):
    genre = db.query(genre_model.Genre).get(id)
    if not genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"genre {id} not available"
        )

    for key, value in update_data.items():
        if hasattr(genre, key):
            if (value is None) and (not genre_model.Genre.__table__.c[key].nullable):
                continue
            setattr(genre, key, value)
    setattr(genre, "updated_at", datetime.utcnow())
    db.commit()
