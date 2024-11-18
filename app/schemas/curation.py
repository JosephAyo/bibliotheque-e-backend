from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from .book import ShowBookPublic


class NoExtraBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class IgnoreExtraBaseModel(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attributes=True)


class CreateCuration(NoExtraBaseModel):
    title: str
    description: str
    published: bool
    book_ids: List[str]


class EditCuration(NoExtraBaseModel):
    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    published: Optional[bool] = None
    book_ids: Optional[List[str]] = []


class BookCurationAssociation(IgnoreExtraBaseModel):
    id: str
    book_id: str
    curation_id: str
    book: ShowBookPublic


class ShowCuration(IgnoreExtraBaseModel):
    id: str
    title: str
    description: str
    curation_associations: List[BookCurationAssociation]
    created_at: datetime
    updated_at: datetime


class ShowCurationPrivate(ShowCuration):
    published: bool


class GetCurationsPublicResponse(IgnoreExtraBaseModel):
    message: str
    data: List[ShowCuration]


class GetCurationsPrivateResponse(IgnoreExtraBaseModel):
    message: str
    data: List[ShowCurationPrivate]
