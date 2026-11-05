from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ResponseBase(BaseModel, Generic[T]):
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None
    error: Optional[str] = None


class SuccessResponse(ResponseBase[T], Generic[T]):
    success: bool = True


class ErrorResponse(ResponseBase):
    success: bool = False
    data: None = None
