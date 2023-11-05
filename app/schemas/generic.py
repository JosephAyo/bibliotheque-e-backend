from pydantic import BaseModel


class NoExtraBaseModel(BaseModel):
    class Config:
        extra = "forbid"


class NoDataResponse(NoExtraBaseModel):
    message: str
    detail: str
