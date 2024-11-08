import pprint
from typing import List
from fastapi import Depends
from sqlalchemy.orm import Session

from ..database.models import (
    book_curation_association as book_curation_association_model,
)
from ..schemas import curation as curation
from ..database.base import get_db
from ..repository import book as book_repository


def create_multiple(
    curation_id: str,
    book_ids: List[str],
    db: Session = Depends(get_db),
):
    existing_associations = (
        db.query(book_curation_association_model.BookCurationAssociation)
        .filter_by(curation_id=curation_id)
        .all()
    )

    existing_book_ids = set(assoc.book_id for assoc in existing_associations)

    valid_book_ids = set(
        book_id for book_id in book_ids if book_repository.get_one(book_id, None, db)
    )

    new_associations = []
    for book_id in valid_book_ids:
        if book_id not in existing_book_ids:
            new_association = book_curation_association_model.BookCurationAssociation(
                curation_id=curation_id, book_id=book_id
            )
            new_associations.append(new_association)

    db.add_all(new_associations)
    db.commit()


def destroy_multiple(ids: List[str], db: Session = Depends(get_db)):
    associations = db.query(
        book_curation_association_model.BookCurationAssociation
    ).filter(book_curation_association_model.BookCurationAssociation.id.in_(ids))
    associations.delete(synchronize_session=False)
    db.commit()
