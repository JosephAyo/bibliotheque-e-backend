from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query

from ..database.models import book_genre_association as book_genre_association_model
from ..schemas import genre as genre
from ..database.base import get_db
from ..repository import genre as genre_repository


def create_multiple(
    book_id: str,
    genre_ids: List[str],
    db: Session = Depends(get_db),
):
    existing_associations = (
        db.query(book_genre_association_model.BookGenreAssociation)
        .filter_by(book_id=book_id)
        .all()
    )

    existing_genre_ids = set(assoc.genre_id for assoc in existing_associations)

    association_limit = 5
    if len(existing_associations) + len(genre_ids) <= association_limit:
        # raise HTTPException(
        #     status_code=status.HTTP_400_BAD_REQUEST,
        #     detail=f"book cannot not have more than {association_limit} genres",
        # )
        valid_genre_ids = set(
            genre_id for genre_id in genre_ids if genre_repository.get_one(genre_id, db, True)
        )
        new_associations = []
        for genre_id in valid_genre_ids:
            if genre_id not in existing_genre_ids:
                new_association = book_genre_association_model.BookGenreAssociation(
                    book_id=book_id, genre_id=genre_id
                )
                new_associations.append(new_association)

    db.add_all(new_associations)
    db.commit()


def destroy_multiple(ids: List[str], db: Session = Depends(get_db)):
    associations = db.query(book_genre_association_model.BookGenreAssociation).filter(
        book_genre_association_model.BookGenreAssociation.id.in_(ids)
    )
    associations.delete(synchronize_session=False)
    db.commit()
