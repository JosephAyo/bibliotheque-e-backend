from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, field_validator


class NoExtraBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class IgnoreExtraBaseModel(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attributes=True)


class CreateGenre(NoExtraBaseModel):
    name: str
    description: str

    @field_validator("name")
    def normalize_name(cls, v):
        return v.lower()


class EditGenre(NoExtraBaseModel):
    id: str
    name: Optional[str] = None
    description: Optional[str] = None


class ShowGenre(IgnoreExtraBaseModel):
    id: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime


class GetGenresResponse(IgnoreExtraBaseModel):
    message: str
    data: List[ShowGenre]


class BookGenreAssociation(IgnoreExtraBaseModel):
    book_id: str
    genre_id: str
    genre: ShowGenre
