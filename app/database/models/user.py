from sqlalchemy import DateTime, Boolean, Column, Enum, Integer, String, Text
from sqlalchemy.orm import relationship
from ..enums import EnumSuspensionStatus
from ..base import Base
import uuid
import datetime


class User(Base):
    __tablename__ = "user"
    id = Column(
        "id", Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True
    )
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(Text)
    is_email_verified = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    country = Column(Text)
    trigger = Column(type_=Enum(EnumSuspensionStatus))
    is_deactivated = Column(Boolean, nullable=False, default=False)
    incorrect_password_attempt_count = Column(Integer)
    otp = Column(Text)
    verification_code = Column(Text)
    reset_password_code = Column(Text)
    verification_code_last_generated_at =  Column(DateTime)
    reset_password_code_last_generated_at =  Column(DateTime)
    last_login =  Column(DateTime)
    password_reset_at =  Column(DateTime)
    created_at =  Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at =  Column(DateTime)
    deactivated_at =  Column(DateTime)

    user_role_associations = relationship(
        "UserRoleAssociation", lazy=False, viewonly=True
    )
