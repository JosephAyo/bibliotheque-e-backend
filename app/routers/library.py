from fastapi import APIRouter, Depends, HTTPException, Query, status
from ..schemas import book as book_schemas
from ..schemas import generic as generic_schemas
from ..repository import book as book_repository
from ..repository import check_in_out as check_in_out_repository
from sqlalchemy.orm import Session
from ..database.base import get_db
from ..repository import authentication as authentication_repository
from ..schemas import check_in_out as check_in_out_schemas


router = APIRouter(prefix="/library/books", tags=["Library"])


@router.get(
    "/",
    response_model=book_schemas.ShowBooksPublicResponse,
    status_code=status.HTTP_200_OK,
)
def view_books(
    db: Session = Depends(get_db),
):
    books = book_repository.get_all(None, db)
    data = {"message": "success", "data": books}
    return data


@router.get(
    "/manager",
    response_model=book_schemas.ShowBooksPrivateResponse,
    status_code=status.HTTP_200_OK,
)
def view_books_as_manager(
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
    "/search/manager",
    response_model=book_schemas.ShowBooksPrivateResponse,
    status_code=status.HTTP_200_OK,
)
def search_for_books_as_manager(
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_manager_user),
    query: str = Query(None, description="Search books by title, author & description"),
):
    books = book_repository.search(current_user, query, db)
    data = {"message": "success", "data": books}
    return data


@router.get(
    "/proprietor",
    response_model=book_schemas.ShowBooksPrivateResponse,
    status_code=status.HTTP_200_OK,
)
def view_proprietor_book_list(
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_proprietor_user),
):
    books = book_repository.get_proprietor_books(current_user, db)
    data = {"message": "success", "data": books}
    return data


@router.get(
    "/borrower",
    response_model=check_in_out_schemas.CheckInOutListResponse,
    status_code=status.HTTP_200_OK,
)
def view_borrowed_books(
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_borrower_user),
):
    check_in_outs = check_in_out_repository.get_all_by_user(current_user, db)
    data = {"message": "success", "data": check_in_outs}
    return data


@router.put(
    "/borrower",
    response_model=check_in_out_schemas.CheckInOutResponse,
    status_code=status.HTTP_200_OK,
)
def borrow_book(
    req_body: check_in_out_schemas.CreateCheckInOut,
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_borrower_user),
):
    check_outs = check_in_out_repository.get_all_check_outs_by_user(
        current_user, db
    )
    num_of_check_outs = len(check_outs)
    if num_of_check_outs > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"you have {num_of_check_outs} book{'s' if num_of_check_outs > 1 else ''} still pending return",
        )
    book = book_repository.get_one(req_body.book_id, None, db)
    if book["current_borrow_count"] >= book["public_shelf_quantity"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"book is not available for borrowing",
        )
    check_out_book = check_in_out_repository.check_out_book(
        req_body, current_user.id, db
    )
    data = {"message": "success", "data": check_out_book}
    return data


@router.patch(
    "/borrower",
    response_model=check_in_out_schemas.CheckInOutResponse,
    status_code=status.HTTP_200_OK,
)
def return_book(
    req_body: check_in_out_schemas.ReturnBook,
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_borrower_user),
):
    books = check_in_out_repository.check_in_book(req_body.id, current_user.id, db)
    data = {"message": "success", "data": books}
    return data
