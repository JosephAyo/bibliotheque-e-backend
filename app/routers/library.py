from datetime import datetime, timedelta
import pprint
from typing import Any, List, Union
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status

from app.database.enums import BorrowStatusFilter
from app.database.models.check_in_out import CheckInOut
from app.database.models.curation import Curation
from app.helpers.email_templates import get_book_due_soon_email, get_book_late_email
from app.helpers.send_email import send_email_background
from app.utils.constants import DUE_DAYS_REMINDER_AT, MAX_BOOK_GENRES_ASSOCIATIONS
from ..repository import genre_association as genre_association_repository
from ..schemas import book as book_schemas
from ..schemas import generic as generic_schemas
from ..schemas import genre as genre_schemas
from ..schemas import curation as curation_schemas
from ..repository import book as book_repository
from ..repository import check_in_out as check_in_out_repository
from ..repository import genre as genre_repository
from ..repository import curation as curation_repository
from ..repository import user as user_repository
from ..repository import curation_association as curation_association_repository
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
def view_books(db: Session = Depends(get_db), genres: str | None = None):
    books = book_repository.get_all(None, genres.split(",") if genres else None, db)
    data = {"message": "success", "data": books}
    return data


@router.get(
    "/id/{id}",
    response_model=Union[
        book_schemas.ShowBookPrivateResponse, book_schemas.ShowBookPublicResponse
    ],
    status_code=status.HTTP_200_OK,
)
def view_book(
    id: str,
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_user_or_none),
):
    book = book_repository.get_one(id, current_user, db)
    response = {"message": "success", "data": book}

    data = (
        book_schemas.ShowBookPrivateResponse(**response)
        if authentication_repository.check_if_manager_user(current_user)
        else book_schemas.ShowBookPublicResponse(**response)
    )
    return data.dict()


@router.get(
    "/manager",
    response_model=book_schemas.ShowBooksPrivateResponse,
    status_code=status.HTTP_200_OK,
)
def view_books_as_manager(
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_manager_user),
    genres: str | None = None,
):
    books = book_repository.get_all(
        current_user, genres.split(",") if genres else None, db
    )
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
    current_user=Depends(authentication_repository.get_current_proprietor_user),
):
    if req_body.genre_ids and len(req_body.genre_ids) > MAX_BOOK_GENRES_ASSOCIATIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"book cannot not have more than {MAX_BOOK_GENRES_ASSOCIATIONS} genres",
        )

    created_book = book_repository.create(
        req_body,
        current_user.id,
        db,
    )

    if req_body.genre_ids and any(genre_id for genre_id in req_body.genre_ids):
        genre_association_repository.create_multiple(
            created_book.id, req_body.genre_ids, db
        )
    return {"message": "success", "data": created_book}


@router.patch("/", response_model=generic_schemas.NoDataResponse)
def edit_book_details(
    req_body: book_schemas.EditBookDetails,
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_manager_user),
):
    id = req_body.id
    book = book_repository.get_one(id, current_user.id, db)
    delattr(req_body, "id")
    book_repository.update(id, dict(req_body), db)
    new_association_genre_ids = req_body.genre_ids
    genres_association_ids_marked_for_delete = []

    if req_body.genre_ids and any(genre_id for genre_id in req_body.genre_ids):
        for book_genre_association in book["genre_associations"]:
            new_association_genre_ids = list(
                filter(
                    lambda genre_id: genre_id != book_genre_association.genre_id,
                    req_body.genre_ids,
                )
            )

            if book_genre_association.genre_id not in req_body.genre_ids:
                genres_association_ids_marked_for_delete.append(
                    book_genre_association.id
                )

    if genres_association_ids_marked_for_delete:
        genre_association_repository.destroy_multiple(
            genres_association_ids_marked_for_delete,
            db,
        )

    if new_association_genre_ids:
        genre_association_repository.create_multiple(
            book["id"],
            new_association_genre_ids,
            db,
        )

    return {"message": "success", "detail": "book details updated"}


@router.delete("/{id}", response_model=generic_schemas.NoDataResponse)
def delete_book(
    id: str,
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_manager_user),
):
    book = book_repository.get_one(id, current_user, db)
    if book["current_borrow_count"] > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"book currently has {book['current_borrow_count']} borrowed cop{'ies' if book['current_borrow_count'] > 1 else 'y'}",
        )
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
    genres: str = Query(
        None, description="Filter books by multiple genre ids separated by comma ',' "
    ),
):
    books = book_repository.search(
        current_user, query, genres.split(",") if genres else None, db
    )
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
    genres: str = Query(
        None, description="Filter books by multiple genre ids separated by comma ',' "
    ),
):
    books = book_repository.search(
        current_user, query, genres.split(",") if genres else None, db
    )
    data = {"message": "success", "data": books}
    return data


@router.patch("/quantity", response_model=generic_schemas.NoDataResponse)
def edit_book_quantity(
    req_body: book_schemas.EditBookQuantity,
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_proprietor_user),
):
    id = req_body.id
    book = book_repository.get_one(id, current_user, db)

    if (
        req_body.public_shelf_quantity is not None
        and req_body.public_shelf_quantity < book["current_borrow_count"]
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"book currently has {book['current_borrow_count']} borrowed cop{'ies' if book['current_borrow_count'] > 1 else 'y'}",
        )
    delattr(req_body, "id")
    total_quantity = book["total_quantity"]
    if (
        req_body.public_shelf_quantity is not None
        and req_body.private_shelf_quantity is not None
    ):
        total_quantity = (
            req_body.public_shelf_quantity + req_body.private_shelf_quantity
        )
    elif (
        req_body.public_shelf_quantity is not None
        and req_body.private_shelf_quantity is None
    ):
        total_quantity = book["private_shelf_quantity"] + req_body.public_shelf_quantity
    elif (
        req_body.private_shelf_quantity is not None
        and req_body.public_shelf_quantity is None
    ):
        total_quantity = book["public_shelf_quantity"] + req_body.private_shelf_quantity
    book_repository.update(
        id, dict(**{**dict(req_body), "total_quantity": total_quantity}), db
    )
    return {"message": "success", "detail": "book quantity updated"}


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


@router.get(
    "/borrower/manager",
    response_model=check_in_out_schemas.CheckInOutListResponse,
    status_code=status.HTTP_200_OK,
)
def view_borrowed_books_as_manager(
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_librarian_user),
    status: BorrowStatusFilter = Query(None, description="borrow status filter"),
):
    check_in_outs = []

    if (not status) or status == BorrowStatusFilter.ALL:
        check_in_outs = check_in_out_repository.get_all(db)
    elif status == BorrowStatusFilter.DUE_SOON:
        check_in_outs = check_in_out_repository.get_all_due_soon_books(
            datetime.utcnow() + timedelta(days=DUE_DAYS_REMINDER_AT),
            db,
        )
    elif status == BorrowStatusFilter.LATE:
        check_in_outs = check_in_out_repository.get_all_late_books(db)
    data = {"message": "success", "data": check_in_outs}
    return data


@router.post(
    "/borrower/manager/{id}",
    response_model=generic_schemas.NoDataResponse,
    status_code=status.HTTP_200_OK,
)
def send_borrowed_books_reminder(
    id: str,
    background_tasks: BackgroundTasks,
    current_user=Depends(authentication_repository.get_current_librarian_user),
    db: Session = Depends(get_db),
):
    check_in_out = check_in_out_repository.get_one(id, db)
    if check_in_out:
        borrower_id = check_in_out.borrower_id
        borrower = user_repository.get_one(
            borrower_id,
            db,
        )
        if borrower:
            today = datetime.utcnow()
            is_late = (
                check_in_out.due_at >= today
                and check_in_out.due_at <= today + timedelta(days=DUE_DAYS_REMINDER_AT)
            )
            is_due_soon = check_in_out.due_at <= today

            if is_due_soon:
                send_email_background(
                    background_tasks,
                    "Your Library Book is Due Soon!",
                    f"{borrower.email}",
                    get_book_due_soon_email(
                        borrower.first_name,
                        check_in_out.book.title,
                        check_in_out.due_at,
                    ),
                )

            if is_late:
                send_email_background(
                    background_tasks,
                    "Your Library Book is Late!",
                    f"{borrower.email}",
                    get_book_late_email(
                        borrower.first_name,
                        check_in_out.book.title,
                        check_in_out.due_at,
                    ),
                )
    return {"message": "success", "detail": "reminder sent"}


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
    check_outs = check_in_out_repository.get_all_check_outs_by_user(current_user, db)
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


@router.get(
    "/borrower/reminders",
    response_model=check_in_out_schemas.CheckInOutReminderResponse,
    status_code=status.HTTP_200_OK,
)
def view_due_soon_and_late_books(
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_borrower_user),
):
    due_soon_checkouts: List[CheckInOut] = (
        check_in_out_repository.get_due_soon_books_by_user(
            current_user, datetime.utcnow() + timedelta(days=DUE_DAYS_REMINDER_AT), db
        )
    )


    late_checkouts: List[CheckInOut] = check_in_out_repository.get_late_books_by_user(
        current_user, db
    )

    return {
        "message": "success",
        "data": {
            "has_due": len(due_soon_checkouts) >= 1,
            "has_late": len(late_checkouts) >= 1,
        },
    }


@router.get(
    "/genres",
    response_model=genre_schemas.GetGenresResponse,
    status_code=status.HTTP_200_OK,
)
def view_genres(
    db: Session = Depends(get_db),
):
    genres = genre_repository.get_all(db)
    data = {"message": "success", "data": genres}
    return data


@router.post(
    "/genres",
    response_model=generic_schemas.NoDataResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_genre(
    req_body: genre_schemas.CreateGenre,
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_manager_user),
):
    existing_genre = genre_repository.get_one_by_name(req_body.name, db, True)
    if existing_genre:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"genre '{req_body.name}' already exists",
        )

    genre_repository.create(
        req_body,
        db,
    )
    return {"message": "success", "detail": "genre created"}


@router.patch("/genres", response_model=generic_schemas.NoDataResponse)
def edit_genre_details(
    req_body: genre_schemas.EditGenre,
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_manager_user),
):
    id = req_body.id
    genre_repository.get_one(id, db)
    delattr(req_body, "id")

    if req_body.name:
        existing_genre = genre_repository.get_one_by_name(req_body.name, db, True)
        if existing_genre and (existing_genre.id != id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"genre '{req_body.name}' already exists",
            )

    genre_repository.update(id, dict(req_body), db)
    return {"message": "success", "detail": "genre details updated"}


@router.get(
    "/curations/{id}",
    response_model=Union[
        curation_schemas.GetCurationPublicResponse,
        curation_schemas.GetCurationPrivateResponse,
    ],
    status_code=status.HTTP_200_OK,
)
def view_curation(
    id: str,
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_user_or_none),
):
    curation: List[Curation] = curation_repository.get_one(id, current_user, db)

    response: dict[str, Any] = {"message": "success", "data": curation}

    data = (
        curation_schemas.GetCurationPrivateResponse(**response)
        if authentication_repository.check_if_manager_user(current_user)
        else curation_schemas.GetCurationPublicResponse(**response)
    )
    return data


@router.get(
    "/curations",
    response_model=Union[
        curation_schemas.GetCurationsPublicResponse,
        curation_schemas.GetCurationsPrivateResponse,
    ],
    status_code=status.HTTP_200_OK,
)
def view_curations(
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_user_or_none),
):
    curations: List[Curation] = curation_repository.get_all(current_user, db)

    curation_dicts = [curation.__dict__ for curation in curations]

    response: dict[str, Any] = {"message": "success", "data": curation_dicts}

    data = (
        curation_schemas.GetCurationsPrivateResponse(**response)
        if authentication_repository.check_if_manager_user(current_user)
        else curation_schemas.GetCurationsPublicResponse(**response)
    )
    return data


@router.post(
    "/curations",
    response_model=generic_schemas.NoDataResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_curation(
    req_body: curation_schemas.CreateCuration,
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_manager_user),
):

    curation = curation_repository.create(
        req_body,
        db,
    )
    curation_association_repository.create_multiple(curation.id, req_body.book_ids, db)

    return {"message": "success", "detail": "curation created"}


@router.put("/curations", response_model=generic_schemas.NoDataResponse)
def edit_curation_details(
    req_body: curation_schemas.EditCuration,
    db: Session = Depends(get_db),
    current_user=Depends(authentication_repository.get_current_manager_user),
):
    id = req_body.id
    curation = curation_repository.get_one(id, current_user, db)
    delattr(req_body, "id")

    curation_repository.update(id, dict(req_body), db)
    if curation is not None:
        new_association_book_ids = req_body.book_ids
        curation_association_ids_marked_for_delete = []

        if req_body.book_ids is not None:
            for curation_association in curation.curation_associations:
                new_association_book_ids = list(
                    filter(
                        lambda book_id: book_id != curation_association.book_id,
                        req_body.book_ids,
                    )
                )

                if curation_association.book_id not in req_body.book_ids:
                    curation_association_ids_marked_for_delete.append(
                        curation_association.id
                    )

        if curation_association_ids_marked_for_delete:
            curation_association_repository.destroy_multiple(
                curation_association_ids_marked_for_delete,
                db,
            )

        if new_association_book_ids:
            curation_association_repository.create_multiple(
                curation.id,
                new_association_book_ids,
                db,
            )
    return {"message": "success", "detail": "curation details updated"}
