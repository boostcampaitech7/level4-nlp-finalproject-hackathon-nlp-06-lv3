from fastapi import Request

from server._core.errors.exceptions.custom_exception import CustomException
from server._core.errors.exceptions.error_code import ErrorCode


async def get_user_id_from_session(request: Request) -> int:
    user_id = request.session.get("user_id")
    if not user_id:  # 세션에 user_id가 없는 경우
        raise CustomException(ErrorCode.UNAUTHORIZED)
    return int(user_id)
