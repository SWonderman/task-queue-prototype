from typing import Iterable, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ResponseWithPagination(BaseModel, Generic[T]):
    current_page: int
    items_count: int
    pages_count: int
    items: Iterable[T]
