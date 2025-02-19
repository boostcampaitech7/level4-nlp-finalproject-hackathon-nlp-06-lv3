from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

from server._core.errors.exceptions.error_code import ErrorCode

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    status: int = 200
    response: Optional[T] = None
    error_message: Optional[str] = None

    @classmethod
    def success(cls, data: T = None, status: int = 200) -> "ApiResponse[T]":
        return cls(status=status, response=data, error_message=None)

    @classmethod
    def error(cls, error_code: ErrorCode, error_message: str) -> "ApiResponse[None]":
        return cls(
            status=error_code.http_status, response=error_code.name, error_message=error_message or error_code.message
        )
