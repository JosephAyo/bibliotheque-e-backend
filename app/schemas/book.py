from typing import List
from pydantic import BaseModel


class NoExtraBaseModel(BaseModel):
    class Config:
        extra = "forbid"


class Book(NoExtraBaseModel):
    id: str
    title: str
    author_name: str
    description: str
    total_quantity: int
    public_shelf_quantity: int
    private_shelf_quantity: int


class ShowBook(NoExtraBaseModel):
    id: str
    title: str
    author_name: str
    description: str


class ShowBookPublic(ShowBook):
    public_shelf_quantity: int


class ShowBookPublicResponse(NoExtraBaseModel):
    message: str
    data: List[ShowBookPublic]


class ShowBookPrivate(ShowBook):
    total_quantity: int
    public_shelf_quantity: int
    private_shelf_quantity: int


class ShowBookPrivateResponse(NoExtraBaseModel):
    message: str
    data: List[ShowBookPrivate]
