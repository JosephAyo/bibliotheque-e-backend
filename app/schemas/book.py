from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict


class NoExtraBaseModel(BaseModel):
    class Config:
        extra = "forbid"


class CreateBook(NoExtraBaseModel):
    title: str
    author_name: str
    description: str
    public_shelf_quantity: int
    private_shelf_quantity: int


class Book(CreateBook):
    id: str
    proprietor_id: str
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    deleted_at: datetime


class ShowBook(NoExtraBaseModel):
    id: str
    title: str
    author_name: str
    description: str
    created_at: datetime
    updated_at: datetime


class ShowBookPublic(ShowBook):
    public_shelf_quantity: int


class ShowBookPublicResponse(NoExtraBaseModel):
    message: str
    data: ShowBookPublic


class ShowBooksPublicResponse(NoExtraBaseModel):
    message: str
    data: List[ShowBookPublic]

    model_config = ConfigDict(from_attributes=True)


class ShowBookPrivate(ShowBook):
    proprietor_id: str
    total_quantity: int
    public_shelf_quantity: int
    private_shelf_quantity: int


class ShowBookPrivateResponse(NoExtraBaseModel):
    message: str
    data: ShowBookPrivate


class ShowBooksPrivateResponse(NoExtraBaseModel):
    message: str
    data: List[ShowBookPrivate]

    model_config = ConfigDict(from_attributes=True)


class EditBook(NoExtraBaseModel):
    id: str
    title: str
    author_name: str
    description: str
    private_shelf_quantity: int
