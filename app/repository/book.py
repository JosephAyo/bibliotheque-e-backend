from typing import List, Union
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database.models import book as book_models
from ..database.base import get_db
from ..schemas import user as user_schemas
from ..schemas import book as book_schemas


def get_all(
    current_user: Union[user_schemas.User, None], db: Session = Depends(get_db)
):
    query = db.query(book_models.Book)

    if current_user is None:
        user_books: List[book_schemas.ShowBookPublic] = query.filter(
            book_models.Book.public_shelf_quantity > 0
        ).all()
        return user_books

    else:
        librarian_and_proprietor_books: List[book_schemas.ShowBookPrivate] = query.all()
        return librarian_and_proprietor_books


def create(
    req_body: book_schemas.CreateBook, user_id: str, db: Session = Depends(get_db)
):
    new_book = book_models.Book(
        proprietor_id=user_id,
        title=req_body.title,
        author_name=req_body.author_name,
        description=req_body.description,
        total_quantity=req_body.public_shelf_quantity + req_body.private_shelf_quantity,
        public_shelf_quantity=req_body.public_shelf_quantity,
        private_shelf_quantity=req_body.private_shelf_quantity,
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


def get_proprietor_book(id: str, proprietor_id: str, db: Session = Depends(get_db)):
    book = (
        db.query(book_models.Book).filter_by(id=id, proprietor_id=proprietor_id).first()
    )
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"book {id} not available"
        )
    return book


def update(id, update_data: dict, db: Session = Depends(get_db)):
    book = db.query(book_models.Book).get(id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"book {id} not available"
        )

    for key, value in update_data.items():
        if hasattr(book, key):
            if (value is None) and (not book_models.Book.__table__.c[key].nullable):
                continue
            setattr(book, key, value)
    db.commit()