from sqlalchemy import DateTime, Boolean, Column, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..base import Base
import uuid
import datetime


class BookCurationAssociation(Base):
    __tablename__ = "book_curation_association"
    id = Column(
        "id", Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True
    )
    book_id = Column(Text(length=36), ForeignKey("book.id"), nullable=False)
    curation_id = Column(Text(length=36), ForeignKey("curation.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)

    curation = relationship(
        "Curation",
        back_populates="curation_associations",
    )
    book = relationship("Book", lazy=False)
