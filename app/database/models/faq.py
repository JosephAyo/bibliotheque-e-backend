from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Text, func
from ..base import Base
import uuid


class Faq(Base):
    __tablename__ = "faq"
    id = Column(
        "id", Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True
    )
    author_id = Column(Text(length=36), ForeignKey("user.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(TIMESTAMP)
