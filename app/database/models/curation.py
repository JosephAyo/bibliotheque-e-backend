from sqlalchemy import (
    DateTime,
    Boolean,
    Column,
    String,
    Text,
)

from ..base import Base
import uuid
import datetime
from sqlalchemy.orm import relationship


class Curation(Base):
    __tablename__ = "curation"
    id = Column(
        "id", Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True
    )
    title = Column(String, nullable=False)
    description = Column(Text)
    published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)

    curation_associations = relationship(
        "BookCurationAssociation",
        lazy=False
    )
