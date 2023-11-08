from sqlalchemy import DateTime, Boolean, Column, ForeignKey, String, Text
from ..base import Base
import uuid
import datetime


class Notification(Base):
    __tablename__ = "notification"
    id = Column(
        "id", Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True
    )
    user_id = Column(Text(length=36), ForeignKey("user.id"))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at =  Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at =  Column(DateTime)
