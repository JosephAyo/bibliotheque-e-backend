from ..database.enums import RolePermission, UserRole
from ..schemas import user as user_schemas
from ..schemas import role as role_schemas
from ..schemas import permission as permission_schemas
from ..database.base import SessionLocal
from ..repository import user as user_repository
from ..repository import role as role_repository
from ..repository import permission as permission_repository
import os
from dotenv import load_dotenv

load_dotenv(".env")


class Envs:
    DEFAULT_USER_EMAIL = os.getenv("DEFAULT_USER_EMAIL")
    DEFAULT_USER_FIRSTNAME = os.getenv("DEFAULT_USER_FIRSTNAME")
    DEFAULT_USER_LASTNAME = os.getenv("DEFAULT_USER_LASTNAME")
    DEFAULT_USER_PASSWORD = os.getenv("DEFAULT_USER_PASSWORD")


default_librarian_data = {
    "first_name": Envs.DEFAULT_USER_FIRSTNAME,
    "last_name": Envs.DEFAULT_USER_LASTNAME,
    "email": Envs.DEFAULT_USER_EMAIL,
    "password": Envs.DEFAULT_USER_PASSWORD,
}


def create_default_roles_and_permissions():
    for role_permission in RolePermission:
        permission = permission_repository.get_one_by_name(
            role_permission.value, SessionLocal(), True
        )
        if permission is None:
            permission = permission_repository.create(
                permission_schemas.CreatePermission(
                    name=role_permission.value, description=role_permission.value
                ),
                SessionLocal(),
            )
    for user_role in UserRole:
        role = role_repository.get_one_by_name(user_role.value, SessionLocal(), True)
        if role is None:
            role = role_repository.create(
                role_schemas.CreateRole(
                    name=user_role.value, description=user_role.value
                ),
                SessionLocal(),
            )
            permission = permission_repository.get_one_by_name(
                RolePermission.ALL.value, SessionLocal(), True
            )
            if permission is not None:
                role_repository.create_role_permission_association(
                    role_schemas.CreateRolePermissionAssociation(
                        **{"role_id": role.id, "permission_id": permission.id}
                    ),
                    SessionLocal(),
                )


def create_default_users():
    if None in default_librarian_data.values() or "" in default_librarian_data.values():
        return
    librarian_user = user_repository.get_one_by_email(
        default_librarian_data["email"], SessionLocal(), True
    )
    if librarian_user is None:
        librarian_user = user_repository.create(
            user_schemas.UserSignUp(**default_librarian_data),
            SessionLocal(),
        )
        user_role = role_repository.get_one_by_name(
            UserRole.LIBRARIAN.value, SessionLocal(), True
        )
        if user_role is not None:
            user_repository.create_user_role_association(
                user_schemas.CreateUserRoleAssociation(
                    **{"user_id": librarian_user.id, "role_id": user_role.id}
                ),
                SessionLocal(),
            )
