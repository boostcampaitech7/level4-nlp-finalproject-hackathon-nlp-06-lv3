from fastapi import HTTPException, Request


async def get_user_id_from_session(request: Request) -> int:
    user_id = request.session.get("user_id")
    if not user_id:  # 세션에 user_id가 없는 경우
        raise HTTPException(status_code=401, detail="Authentication required. Please log in.")  # Unauthorized
    return int(user_id)
