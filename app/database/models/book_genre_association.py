from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Text, func
from base import Base
import uuid


class BookGenreAssociation(Base):
    __tablename__ = "book_genre_association"
    id = Column(
        "id", Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True
    )
    book_id = Column(Text(length=36), ForeignKey("book.id"), nullable=False)
    genre_id = Column(Text(length=36), ForeignKey("genre.id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(TIMESTAMP)
