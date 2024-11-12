from datetime import datetime, timedelta
from typing import List

from sqlalchemy import Column

from app.database.models.check_in_out import CheckInOut
from app.database.models.user import User
from app.helpers.email_templates import get_book_due_soon_email, get_book_late_email
from app.utils.constants import DUE_DAYS_REMINDER_AT
from ..repository import user as user_repository
from ..database.base import SessionLocal
from ..helpers.send_email import send_email_async

from app.repository.check_in_out import get_all_due_soon_books, get_all_late_books


async def send_due_soon_reminders():
    due_time = datetime.utcnow() + timedelta(days=DUE_DAYS_REMINDER_AT)

    check_outs: List[CheckInOut] = get_all_due_soon_books(due_time, SessionLocal())

    # Iterate over the books and send emails
    for check_out in check_outs:
        borrower_id: Column[str] = check_out.borrower_id
        borrower: User | None = user_repository.get_one(
            borrower_id, SessionLocal(), True
        )

        if borrower:
            await send_email_async(
                "Your Library Book is Due Soon!",
                f"{borrower.email}",
                get_book_due_soon_email(
                    borrower.first_name, check_out.book.title, check_out.due_at
                ),
            )


async def send_late_reminders():
    check_outs: List[CheckInOut] = get_all_late_books(SessionLocal())

    # Iterate over the books and send emails
    for check_out in check_outs:
        borrower_id: Column[str] = check_out.borrower_id
        borrower: User | None = user_repository.get_one(
            borrower_id, SessionLocal(), True
        )

        if borrower:
            await send_email_async(
                "Your Library Book is Late!",
                f"{borrower.email}",
                get_book_late_email(
                    borrower.first_name, check_out.book.title, check_out.due_at
                ),
            )
