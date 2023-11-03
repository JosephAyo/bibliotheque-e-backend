from typing import Union
from fastapi import Depends
from sqlalchemy.orm import Session
from ..database.models import book as book_models
from ..database.base import get_db
from ..schemas import user as user_schemas


def get_all(
    current_user: Union[user_schemas.User, None], db: Session = Depends(get_db)
):
    if current_user is None:
        books = (
            db.query(book_models.Book)
            .filter(book_models.Book.public_shelf_quantity > 0)
            .all()
        )
    else:
        books = db.query(book_models.Book).all()
    return books
