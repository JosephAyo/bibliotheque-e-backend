from typing import Union
from fastapi import Depends, HTTPException, status
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session
from ..database.models import book as book_models
from ..database.base import get_db
from ..schemas import user as user_schemas
from ..schemas import book as book_schemas
from ..database.models import check_in_out as check_in_out_models
from datetime import datetime


def get_book_query_base(db: Session = Depends(get_db)):
    return (
        db.query(
            book_models.Book,
            func.count(check_in_out_models.CheckInOut.id).label("current_borrow_count"),
        )
        .join(
            check_in_out_models.CheckInOut,
            and_(
                check_in_out_models.CheckInOut.book_id == book_models.Book.id,
                check_in_out_models.CheckInOut.returned == False,
            ),
            isouter=True,
        )
        .group_by(book_models.Book.id)
    )


def get_all(
    current_user: Union[user_schemas.User, None], db: Session = Depends(get_db)
):
    query = get_book_query_base(db).order_by(book_models.Book.updated_at.desc())

    if current_user is None:
        user_books = query.filter(book_models.Book.public_shelf_quantity > 0).all()

        books = [
            {
                **row._asdict()["Book"].__dict__,
                "current_borrow_count": row._asdict()["current_borrow_count"],
            }
            for row in user_books
        ]

    else:
        # NOTE: this is how to join and select
        # librarian_and_proprietor_books: List[
        #     book_schemas.ShowBookPrivate
        # ] = query.options(
        #     joinedload(
        #         book_models.Book.check_in_outs,
        #     ),
        # ).all()
        librarian_and_proprietor_books = query.all()
        books = [
            {
                **row._asdict()["Book"].__dict__,
                "current_borrow_count": row._asdict()["current_borrow_count"],
            }
            for row in librarian_and_proprietor_books
        ]
    return books


def get_one(
    id: str, current_user: Union[user_schemas.User, None], db: Session = Depends(get_db)
):
    query = get_book_query_base(db)

    if current_user is None:
        book = query.filter(
            and_(book_models.Book.public_shelf_quantity > 0, book_models.Book.id == id)
        ).first()
    else:
        book = query.filter(book_models.Book.id == id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"book {id} not available"
        )
    return {
        **book._asdict()["Book"].__dict__,
        "current_borrow_count": book._asdict()["current_borrow_count"],
    }


def search(
    current_user: Union[user_schemas.User, None],
    search_string: str,
    db: Session = Depends(get_db),
):
    query = (
        get_book_query_base(db)
        .order_by(book_models.Book.updated_at.desc())
        .filter(
            or_(
                book_models.Book.title.ilike(f"%{search_string}%"),
                book_models.Book.author_name.ilike(f"%{search_string}%"),
                book_models.Book.description.ilike(f"%{search_string}%"),
            )
        )
    )

    if current_user is None:
        user_books = query.filter(book_models.Book.public_shelf_quantity > 0).all()
        books = [
            {
                **row._asdict()["Book"].__dict__,
                "current_borrow_count": row._asdict()["current_borrow_count"],
            }
            for row in user_books
        ]

    else:
        librarian_and_proprietor_books = query.all()
        books = [
            {
                **row._asdict()["Book"].__dict__,
                "current_borrow_count": row._asdict()["current_borrow_count"],
            }
            for row in librarian_and_proprietor_books
        ]
    return books


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
        get_book_query_base(db)
        .order_by(book_models.Book.updated_at.desc())
        .filter_by(id=id, proprietor_id=proprietor_id)
        .first()
    )
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"book {id} not available"
        )
    return {
        **book._asdict()["Book"].__dict__,
        "current_borrow_count": book._asdict()["current_borrow_count"],
    }


def get_proprietor_books(
    current_user: user_schemas.User, db: Session = Depends(get_db)
):
    query = (
        get_book_query_base(db)
        .filter_by(proprietor_id=current_user.id)
        .order_by(book_models.Book.updated_at.desc())
    )

    proprietor_books = query.all()
    books = [
        {
            **row._asdict()["Book"].__dict__,
            "current_borrow_count": row._asdict()["current_borrow_count"],
        }
        for row in proprietor_books
    ]
    return books


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
    setattr(book, "updated_at", datetime.utcnow())
    db.commit()


def destroy(id, db: Session = Depends(get_db)):
    book = db.query(book_models.Book).filter_by(id=id)
    if not book.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"book {id} not available"
        )
    book.delete(synchronize_session=False)
    db.commit()
