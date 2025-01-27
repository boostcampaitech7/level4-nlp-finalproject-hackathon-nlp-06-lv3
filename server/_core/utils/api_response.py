from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    status: int = 200
    data: Optional[T] = None
    error_message: Optional[str] = None

    @classmethod
    def success(cls, data: T = None, status: int = 200) -> "ApiResponse[T]":
        return cls(status=status, data=data, error_message=None)

    @classmethod
    def error(cls, error_message: str, status: int = 400) -> "ApiResponse[None]":
        return cls(status=status, data=None, error_message=error_message)
