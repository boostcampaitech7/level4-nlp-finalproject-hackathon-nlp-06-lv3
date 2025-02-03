from fastapi import APIRouter, Depends, Request

from server._core.dependencies.session import get_user_id_from_session
from server._core.utils.api_response import ApiResponse
from server.models.user import User
from server.schemas import auth_request, auth_response
from server.service import auth_service

# Initialize router
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.get("/is-login")
async def is_login(request: Request) -> ApiResponse[auth_response.IsLoginDto]:
    user_id = request.session.get("user_id")
    return ApiResponse.success(auth_service.is_login(user_id))


@auth_router.post("/logout")
async def logout(request: Request) -> ApiResponse:
    request.session.clear()
    return ApiResponse.success()


@auth_router.post("/google")
async def google_auth(
    request_dto: auth_request.GoogleAuthDto, request: Request
) -> ApiResponse[auth_response.GoogleAuthDto]:
    response_dto, user_id = await auth_service.google_authenticatie(request_dto)
    request.session["user_id"] = user_id
    return ApiResponse.success(response_dto)


@auth_router.get("/google/profile")
async def google_profile(
    user: User = Depends(get_user_id_from_session),
) -> ApiResponse[auth_response.GoogleProfileDto]:
    return ApiResponse.success(await auth_service.get_google_profile(user))


@auth_router.get("/google/callback")
async def google_callback(code: str) -> ApiResponse[auth_response.GoogleCallbackDto]:
    return ApiResponse.success(auth_service.google_callback(code))
