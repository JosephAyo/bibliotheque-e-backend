from datetime import datetime
from typing import Annotated, List, Optional
from annotated_types import Ge
from pydantic import BaseModel, ConfigDict, root_validator


class NoExtraBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class IgnoreExtraBaseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class CreateBook(NoExtraBaseModel):
    title: str
    author_name: str
    description: str
    public_shelf_quantity: Annotated[int, Ge(0)]
    private_shelf_quantity: Annotated[int, Ge(1)]


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
    data: ShowBookPublicWithBorrowCount


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
    data: ShowBookPrivateWithBorrowCount


class ShowBooksPrivateResponse(IgnoreExtraBaseModel):
    message: str
    data: List[ShowBookPrivateWithBorrowCount]


class EditBookDetails(NoExtraBaseModel):
    id: str
    title: Optional[str] = None
    author_name: Optional[str] = None
    description: Optional[str] = None


class EditBookQuantity(NoExtraBaseModel):
    id: str
    public_shelf_quantity: Annotated[Optional[int], Ge(0)] = None
    private_shelf_quantity: Annotated[Optional[int], Ge(0)] = None

    @root_validator(pre=True)
    def check_public_shelf_quantity_or_private_shelf_quantity(cls, values):
        if (values.get("public_shelf_quantity") is None) and (
            values.get("private_shelf_quantity") is None
        ):
            raise ValueError(
                "either public_shelf_quantity or private_shelf_quantity is required"
            )
        return values
