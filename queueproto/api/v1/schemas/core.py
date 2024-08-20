from typing import Iterable, Generic, TypeVar, List
from pydantic import BaseModel

T = TypeVar("T")


class ResponseWithPagination(BaseModel, Generic[T]):
    current_page: int
    items_count: int
    pages_count: int
    items: Iterable[T]


class Error(BaseModel):
   message: str


class ErrorResponse(BaseModel):
    errors: List[Error]
