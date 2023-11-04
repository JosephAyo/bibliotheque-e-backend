from typing import List, Union
from fastapi import Depends
from sqlalchemy.orm import Session, defer
from ..database.models import book as book_models
from ..database.base import get_db
from ..schemas import user as user_schemas
from ..schemas import book as book_schemas


def get_all(
    current_user: Union[user_schemas.User, None], db: Session = Depends(get_db)
):
    query = db.query(book_models.Book)

    if current_user is None:
        columns_to_exclude = [
            "private_shelf_quantity",
            "total_quantity",
            "proprietor_id",
            "is_deleted",
            "deleted_at",
        ]
        for column_name in columns_to_exclude:
            query = query.options(defer(getattr(book_models.Book, column_name)))

        user_books: List[book_schemas.ShowBookPublic] = query.filter(
            book_models.Book.public_shelf_quantity > 0
        ).all()
        return user_books

    else:
        columns_to_exclude = [
            "is_deleted",
            "deleted_at",
        ]
        for column_name in columns_to_exclude:
            query = query.options(defer(getattr(book_models.Book, column_name)))

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
