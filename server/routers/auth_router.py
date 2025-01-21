import os

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from server.service import auth_service

# Load environment variables
load_dotenv()

# Google OAuth2 setup
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:3000"

# Initialize router
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


class GoogleAuthRequest(BaseModel):
    code: str


@auth_router.post("/google")
async def google_auth(request_body: GoogleAuthRequest, request: Request):
    user_id = await auth_service.google_authenticatie(request_body.code)
    request.session["user_id"] = user_id
    return {"user_id": user_id}


@auth_router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return {"message": "Logged out"}


class ValidateTokenRequest(BaseModel):
    access_token: str


@auth_router.post("/google/validate-token")
async def validate_token(request_body: ValidateTokenRequest):
    return auth_service.get_token_info(request_body.access_token)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@auth_router.get("/google/profile")
async def google_profile(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:  # 세션에 user_id가 없는 경우
        raise HTTPException(status_code=401, detail="Authentication required. Please log in.")  # Unauthorized
    return await auth_service.get_google_profile(user_id)
