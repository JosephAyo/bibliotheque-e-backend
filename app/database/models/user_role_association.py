from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from ..base import Base
import uuid


class UserRoleAssociation(Base):
    __tablename__ = "user_role_association"
    id = Column(
        "id", Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True
    )
    user_id = Column(Text(length=36), ForeignKey("user.id"), nullable=False)
    role_id = Column(Text(length=36), ForeignKey("role.id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(TIMESTAMP)

    users = relationship("User", lazy=False)
    role = relationship("Role",  lazy=False)
