from sqlalchemy import JSON, TIMESTAMP, Boolean, Column, ForeignKey, Text, func
from ..base import Base
import uuid


class AppLog(Base):
    __tablename__ = "app_log"
    id = Column(
        "id", Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True
    )
    user_id = Column(Text(length=36), ForeignKey("user.id"), nullable=False)
    details = Column(JSON, nullable=False)
    description = Column(Text)
    requires_action = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(TIMESTAMP)
