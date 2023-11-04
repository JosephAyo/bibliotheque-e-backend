from typing import Union
from fastapi import APIRouter, Depends, status
from ..schemas import book as book_schemas
from ..repository import book as book_repository
from sqlalchemy.orm import Session
from ..database.base import get_db
from ..repository import authentication as authentication_repository


router = APIRouter(prefix="/library/books", tags=["Library"])


@router.get(
    "/",
    response_model=Union[
        book_schemas.ShowBooksPrivateResponse,
        book_schemas.ShowBooksPublicResponse,
    ],
    # response_model=book_schemas.ShowBooksPrivateResponse,
    status_code=status.HTTP_200_OK,
)
def view_books(
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_user_or_none),
):
    books = book_repository.get_all(current_user, db)
    return {"message": "success", "data": books}


@router.post(
    "/",
    response_model=book_schemas.ShowBookPrivateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_book(
    req_body: book_schemas.CreateBook,
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_user),
):
    created_book = book_repository.create(
        req_body,
        current_user.id,
        db,
    )
    return {"message": "success", "data": created_book}
