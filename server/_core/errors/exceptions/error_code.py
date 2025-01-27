from enum import Enum

from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)


class ErrorCode(Enum):
    UNAUTHORIZED = (HTTP_401_UNAUTHORIZED, "인증되지 않았습니다.")
    PERMISSION_DENIED = (HTTP_403_FORBIDDEN, "권한이 없습니다.")
    NOT_FOUND_USER = (HTTP_404_NOT_FOUND, "존재하지 않는 사용자입니다.")
    NOT_FOUND_DATA = (HTTP_404_NOT_FOUND, "존재하지 않는 데이터에 대한 접근입니다")
    LOGIN_FAILED = (HTTP_400_BAD_REQUEST, "로그인에 실패하였습니다.")
    INVALID_REQUEST_DATA = (HTTP_400_BAD_REQUEST, "올바른 양식이 아닙니다.")
    DUPLICATED_DATA = (HTTP_409_CONFLICT, "이미 존재하는 데이터입니다.")
    REFERENCED_DATA_EXISTS = (HTTP_409_CONFLICT, "사용되고 있는 데이터입니다.")
    SERVER_ERROR = (HTTP_500_INTERNAL_SERVER_ERROR, "서버 오류입니다. 다시 시도해주세요.")
    UNKNOWN_SERVER_ERROR = (HTTP_500_INTERNAL_SERVER_ERROR, "알 수 없는 서버 내부 에러입니다.")

    def __init__(self, http_status: int, message: str):
        self.http_status = http_status
        self.message = message
