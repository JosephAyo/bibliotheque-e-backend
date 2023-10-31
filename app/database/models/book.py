from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)

from base import Base
import uuid


class Book(Base):
    __tablename__ = "book"
    id = Column(
        "id", Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True
    )
    proprietor_id = Column(Text(length=36), ForeignKey("user.id"), nullable=False)
    title = Column(String, nullable=False)
    author_name = Column(String, nullable=False)
    description = Column(Text)
    total_quantity = Column(Integer, nullable=False, default=0)
    public_shelf_quantity = Column(Integer, nullable=False, default=0)
    private_shelf_quantity = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(TIMESTAMP)
