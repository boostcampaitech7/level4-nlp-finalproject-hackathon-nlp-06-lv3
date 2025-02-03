from fastapi import Request

from server._core.errors.exceptions.custom_exception import CustomException
from server._core.errors.exceptions.error_code import ErrorCode
from server.database.connection import database
from server.models.user import User


async def get_user_id_from_session(request: Request) -> User:
    user_id = request.session.get("user_id")
    if not user_id:  # 세션에 user_id가 없는 경우
        raise CustomException(ErrorCode.UNAUTHORIZED)
    user = await database.fetch_one("SELECT * FROM user_tb WHERE id = :id", {"id": user_id})
    if not user:  # 세션에 저장된 user_id가 유효하지 않은 경우
        request.session.clear()
        raise CustomException(ErrorCode.NOT_FOUND_USER)
    return user
