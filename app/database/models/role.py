from sqlalchemy import DateTime, Boolean, Column, String, Text
from ..base import Base
import uuid
import datetime


class Role(Base):
    __tablename__ = "role"
    id = Column(
        "id", Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True
    )
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    created_at =  Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at =  Column(DateTime)
