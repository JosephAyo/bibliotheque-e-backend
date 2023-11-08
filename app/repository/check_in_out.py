from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..database.models import check_in_out as check_in_out_models
from ..database.base import get_db
from ..schemas import user as user_schemas
from ..schemas import check_in_out as check_in_out_schemas
from sqlalchemy import and_


def get_all_by_user(current_user: user_schemas.User, db: Session = Depends(get_db)):
    return (
        db.query(check_in_out_models.CheckInOut)
        .filter_by(borrower_id=current_user.id)
        .order_by(check_in_out_models.CheckInOut.updated_at.desc())
        .all()
    )


def get_one_by_user(
    id: str, current_user: user_schemas.User, db: Session = Depends(get_db)
):
    return (
        db.query(check_in_out_models.CheckInOut)
        .filter_by(
            and_(
                check_in_out_models.CheckInOut.id == id,
                check_in_out_models.CheckInOut.borrower_id == current_user.id,
            )
        )
        .first()
    )


def check_out_book(
    req_body: check_in_out_schemas.CreateCheckInOut,
    user_id: str,
    db: Session = Depends(get_db),
):
    new_check_in_out = check_in_out_models.CheckInOut(
        borrower_id=user_id,
        book_id=req_body.book_id,
        checked_out_at=datetime.utcnow(),
        due_at=datetime.utcnow() + timedelta(days=45),
    )
    db.add(new_check_in_out)
    db.commit()
    db.refresh(new_check_in_out)
    return new_check_in_out


def check_in_book(id: str, user_id: str, db: Session = Depends(get_db)):
    check_in_out = (
        db.query(check_in_out_models.CheckInOut)
        .filter(
            and_(
                check_in_out_models.CheckInOut.id == id,
                check_in_out_models.CheckInOut.borrower_id == user_id,
            )
        )
        .first()
    )
    if not check_in_out:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"check in\out {id} not available",
        )

    setattr(check_in_out, "returned", True)
    setattr(check_in_out, "returned_at", datetime.utcnow())
    setattr(check_in_out, "updated_at", datetime.utcnow())
    db.commit()

    db.refresh(check_in_out)
    return check_in_out


def destroy(id, db: Session = Depends(get_db)):
    check_in_out = db.query(check_in_out_models.CheckInOut).filter_by(id=id)
    if not check_in_out.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"book {id} not available"
        )
    check_in_out.delete(synchronize_session=False)
    db.commit()
