from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from .book import ShowBookPublic


class NoExtraBaseModel(BaseModel):
    class Config:
        extra = "forbid"


class CreateCheckInOut(NoExtraBaseModel):
    book_id: str


class ShowCheckInOut(CreateCheckInOut):
    id: str
    borrower_id: str
    checked_out_at: datetime
    due_at: datetime
    returned: bool
    returned_at: Optional[datetime] = None
    fine_owed: Optional[float] = 0
    fine_paid: Optional[float] = 0
    created_at: datetime
    updated_at: datetime
    book: ShowBookPublic


class CheckInOutResponse(NoExtraBaseModel):
    message: str
    data: ShowCheckInOut


class CheckInOutListResponse(NoExtraBaseModel):
    message: str
    data: List[ShowCheckInOut]


class ReturnBook(NoExtraBaseModel):
    id: str

class ReminderData(NoExtraBaseModel):
    has_due: bool
    has_late: bool

class CheckInOutReminderResponse(NoExtraBaseModel):
    message: str
    data: ReminderData
