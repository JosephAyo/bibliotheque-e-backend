from sqlalchemy import DateTime, Boolean, Column, ForeignKey, Text
from ..base import Base
import uuid
import datetime


class Faq(Base):
    __tablename__ = "faq"
    id = Column(
        "id", Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True
    )
    author_id = Column(Text(length=36), ForeignKey("user.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at =  Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at =  Column(DateTime)
