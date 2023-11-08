from sqlalchemy import DECIMAL, TIMESTAMP, Boolean, Column, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from ..base import Base
import uuid


class CheckInOut(Base):
    __tablename__ = "check_in_out"
    id = Column(
        "id", Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True
    )
    book_id = Column(Text(length=36), ForeignKey("book.id"), nullable=False)
    borrower_id = Column(Text(length=36), ForeignKey("user.id"), nullable=False)
    checked_out_at = Column(TIMESTAMP, nullable=False)
    due_at = Column(TIMESTAMP, nullable=False)
    returned = Column(Boolean, default=False)
    returned_at = Column(TIMESTAMP)
    fine_owed = Column(DECIMAL, nullable=False, default=0)
    fine_paid = Column(DECIMAL, nullable=False, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(TIMESTAMP)

    book = relationship("Book", lazy=False, back_populates="check_in_outs")
