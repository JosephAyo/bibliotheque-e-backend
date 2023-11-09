from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class NoExtraBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class IgnoreExtraBaseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


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


class ShowBook(IgnoreExtraBaseModel):
    id: str
    title: str
    author_name: str
    description: str
    created_at: datetime
    updated_at: datetime


class ShowBookPublic(ShowBook):
    public_shelf_quantity: int


class ShowBookPublicWithBorrowCount(ShowBookPublic):
    current_borrow_count: Optional[int] = 0


class ShowBookPublicResponse(IgnoreExtraBaseModel):
    message: str
    data: ShowBookPublic


class ShowBooksPublicResponse(IgnoreExtraBaseModel):
    message: str
    data: List[ShowBookPublicWithBorrowCount]


class ShowBookPrivate(ShowBook):
    proprietor_id: str
    total_quantity: int
    public_shelf_quantity: int
    private_shelf_quantity: int


class ShowBookPrivateWithBorrowCount(ShowBookPrivate):
    current_borrow_count: Optional[int] = 0


class ShowBookPrivateResponse(IgnoreExtraBaseModel):
    message: str
    data: ShowBookPrivate


class ShowBooksPrivateResponse(IgnoreExtraBaseModel):
    message: str
    data: List[ShowBookPrivate]


class EditBook(NoExtraBaseModel):
    id: str
    title: str
    author_name: str
    description: str
    private_shelf_quantity: int
