from ..database.base import SessionLocal
from ..repository import user as user_repository
from ..repository import book as book_repository
from ..schemas import book as book_schemas
import os
from dotenv import load_dotenv

load_dotenv(".env")
from faker import Faker


fake = Faker()


class Envs:
    DEFAULT_USER_EMAIL = os.getenv("DEFAULT_USER_EMAIL")


authors = [
    "Arthur Conan Doyle",
    "George Orwell",
    "Agatha Christie",
    "Chinua Achebe",
    "Wole Soyinka",
    "Chimamanda Ngozi Adichie",
]


def create_default_books():
    default_user = user_repository.get_one_by_email(
        Envs.DEFAULT_USER_EMAIL, SessionLocal(), True
    )
    if default_user is None:
        return
    book_count = book_repository.count_all(SessionLocal())
    if book_count >= 12:
        return
    for author in authors:
        book_repository.create(
            book_schemas.CreateBook(
                **{
                    "title": fake.catch_phrase(),
                    "author_name": author,
                    "description": fake.text(max_nb_chars=200),
                    "img_url": "https://picsum.photos/200",
                    "public_shelf_quantity": fake.random_int(min=5, max=300),
                    "private_shelf_quantity": fake.random_int(min=1, max=10),
                }
            ),
            default_user.id,
            SessionLocal(),
        )
