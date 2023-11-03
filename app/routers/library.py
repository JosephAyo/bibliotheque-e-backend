from typing import Union
from fastapi import APIRouter, Depends
from ..schemas import book as book_schemas
from ..repository import book as book_repository
from sqlalchemy.orm import Session
from ..database.base import get_db
from ..repository import authentication as authentication_repository


router = APIRouter(prefix="/library/books", tags=["Library"])


@router.get(
    "/",
    response_model=Union[
        book_schemas.ShowBookPublicResponse, book_schemas.ShowBookPrivateResponse
    ],
)
def view_books(
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_user_or_none),
):
    books = book_repository.get_all(current_user, db)
    return {"message": "success", "data": books}
