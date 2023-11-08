from sqlalchemy import DECIMAL, DateTime, Boolean, Column, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..base import Base
import uuid
import datetime



class CheckInOut(Base):
    __tablename__ = "check_in_out"
    id = Column(
        "id", Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True
    )
    book_id = Column(Text(length=36), ForeignKey("book.id"), nullable=False)
    borrower_id = Column(Text(length=36), ForeignKey("user.id"), nullable=False)
    checked_out_at =  Column(DateTime, nullable=False)
    due_at =  Column(DateTime, nullable=False)
    returned = Column(Boolean, default=False)
    returned_at =  Column(DateTime)
    fine_owed = Column(DECIMAL, nullable=False, default=0)
    fine_paid = Column(DECIMAL, nullable=False, default=0)
    created_at =  Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at =  Column(DateTime)

    book = relationship("Book", lazy=False, back_populates="check_in_outs")
