from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    message: str


class PaginationParams(BaseModel):
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)


class PaginationInfo(PaginationParams):
    count: int = Field(0, ge=0)


class DataListResponse[T](BaseModel):
    data: list[T]
    pagination: PaginationInfo
