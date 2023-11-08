from sqlalchemy import DateTime, Boolean, Column, Enum, ForeignKey, Text

from ..enums import EnumSuspensionLogAction, EnumSuspensionStatus
from ..base import Base
import uuid
import datetime


class SuspensionLog(Base):
    __tablename__ = "suspension_log"
    id = Column(
        "id", Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True
    )
    user_id = Column(Text(length=36), ForeignKey("user.id"))
    action = Column(type_=Enum(EnumSuspensionLogAction))
    trigger = Column(type_=Enum(EnumSuspensionStatus))
    reason = Column(Text)
    created_at =  Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at =  Column(DateTime)
