from fastapi import HTTPException

from server._core.errors.exceptions.error_code import ErrorCode


class CustomException(HTTPException):
    def __init__(self, error_code: ErrorCode, error_message: str = None):
        super().__init__(status_code=error_code.http_status, detail=error_message or error_code.message)
        self.error_code = error_code
