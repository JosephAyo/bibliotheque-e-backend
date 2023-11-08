from sqlalchemy import DateTime, Boolean, Column, ForeignKey, Text
from ..base import Base
import uuid
import datetime


class RolePermissionAssociation(Base):
    __tablename__ = "role_permission_association"
    id = Column(
        "id", Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True
    )
    role_id = Column(Text(length=36), ForeignKey("role.id"), nullable=False)
    permission_id = Column(Text(length=36), ForeignKey("permission.id"), nullable=False)
    created_at =  Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at =  Column(DateTime)
