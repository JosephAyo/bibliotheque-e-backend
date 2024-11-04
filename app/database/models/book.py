from sqlalchemy import (
    DateTime,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from ..base import Base
import uuid
import datetime


class Book(Base):
    __tablename__ = "book"
    id = Column(
        "id", Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True
    )
    proprietor_id = Column(Text(length=36), ForeignKey("user.id"), nullable=False)
    title = Column(String, nullable=False)
    author_name = Column(String, nullable=False)
    description = Column(Text)
    img_url = Column(Text)
    total_quantity = Column(Integer, nullable=False, default=0)
    public_shelf_quantity = Column(Integer, nullable=False, default=0)
    private_shelf_quantity = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)

    check_in_outs = relationship("CheckInOut")
    genre_associations = relationship(
        "BookGenreAssociation",
        lazy=False,
    )
