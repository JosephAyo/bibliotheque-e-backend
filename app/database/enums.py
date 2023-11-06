from enum import Enum


class EnumSuspensionLogAction(Enum):
    SUSPENDED = "suspended"
    RESTORED = "restored"


class EnumSuspensionStatus(Enum):
    ADMIN_ACTION = "admin_action"
    PASSWORD_ATTEMPT = "password_attempt"
    TERMS_OF_SERVICE_VIOLATION = "terms_of_service_violation"


class UserRole(Enum):
    BORROWER = "borrower"
    PROPRIETOR = "lender"
    LIBRARIAN = "librarian"


class RolePermission(Enum):
    ALL = "all"