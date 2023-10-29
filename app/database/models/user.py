from sqlalchemy import TIMESTAMP, Boolean, Column, Enum, Integer, String, Text, func
from ..base import Base
import uuid

enum_suspension_status = Enum(
    "admin_action",
    "password_attempt",
    "terms_of_service_violation",
    name="enum_suspension_status",
)


class User(Base):
    __tablename__ = "user"
    id = Column(
        "id", Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True
    )
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(Text)
    is_email_verified = Column(Boolean)
    is_verified = Column(Boolean)
    country = Column(Text)
    suspension_status = Column(enum_suspension_status)
    is_deactivated = Column(Boolean, nullable=False, default=False)
    incorrect_password_attempt_count = Column(Integer)
    otp = Column(Text)
    verification_code = Column(Text)
    reset_password_code = Column(Text)
    verification_code_last_generated_at = Column(TIMESTAMP)
    reset_password_code_last_generated_at = Column(TIMESTAMP)
    last_login = Column(TIMESTAMP)
    password_reset_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    deleted_at = Column(TIMESTAMP)
    deactivated_at = Column(TIMESTAMP)
