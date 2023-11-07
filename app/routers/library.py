from fastapi import APIRouter, Depends, Query, status
from ..schemas import book as book_schemas
from ..schemas import generic as generic_schemas
from ..repository import book as book_repository
from sqlalchemy.orm import Session
from ..database.base import get_db
from ..repository import authentication as authentication_repository


router = APIRouter(prefix="/library/books", tags=["Library"])


@router.get(
    "/",
    response_model=book_schemas.ShowBooksPublicResponse,
    status_code=status.HTTP_200_OK,
)
def view_books(
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_user_or_none),
):
    books = book_repository.get_all(current_user, db)
    data = {"message": "success", "data": books}
    return data


@router.get(
    "/managed",
    response_model=book_schemas.ShowBooksPrivateResponse,
    status_code=status.HTTP_200_OK,
)
def view_managed_books(
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_manager_user),
):
    books = book_repository.get_all(current_user, db)
    data = {"message": "success", "data": books}
    return data


@router.post(
    "/",
    response_model=book_schemas.ShowBookPrivateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_book(
    req_body: book_schemas.CreateBook,
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_manager_user),
):
    created_book = book_repository.create(
        req_body,
        current_user.id,
        db,
    )
    return {"message": "success", "data": created_book}


@router.patch("/", response_model=generic_schemas.NoDataResponse)
def edit_book(
    req_body: book_schemas.EditBook,
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_manager_user),
):
    id = req_body.id
    book_repository.get_proprietor_book(id, current_user.id, db)
    delattr(req_body, "id")
    book_repository.update(id, dict(req_body), db)
    return {"message": "success", "detail": "book updated"}


@router.delete("/{id}", response_model=generic_schemas.NoDataResponse)
def delete_book(
    id: str,
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_manager_user),
):
    book_repository.get_proprietor_book(id, current_user.id, db)
    book_repository.destroy(id, db)
    return {"message": "success", "detail": "book deleted"}


@router.get(
    "/search",
    response_model=book_schemas.ShowBooksPublicResponse,
    status_code=status.HTTP_200_OK,
)
def search_for_books(
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_user_or_none),
    query: str = Query(None, description="Search books by title, author & description"),
):
    books = book_repository.search(current_user, query, db)
    data = {"message": "success", "data": books}
    return data


@router.get(
    "/search/managed",
    response_model=book_schemas.ShowBooksPrivateResponse,
    status_code=status.HTTP_200_OK,
)
def search_for_managed_books(
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_manager_user),
    query: str = Query(None, description="Search books by title, author & description"),
):
    books = book_repository.search(current_user, query, db)
    data = {"message": "success", "data": books}
    return data
