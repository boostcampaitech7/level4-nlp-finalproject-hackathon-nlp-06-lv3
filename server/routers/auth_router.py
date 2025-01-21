from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from server.dependencies.session import get_user_id_from_session
from server.service import auth_service

# Initialize router
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.get("/is-login")
async def is_login(request: Request):
    user_id = request.session.get("user_id")
    return {"is_login": bool(user_id), "user_id": user_id}


class GoogleAuthRequest(BaseModel):
    code: str
    redirect_uri: str


@auth_router.post("/google")
async def google_auth(request_body: GoogleAuthRequest, request: Request):
    user_id = await auth_service.google_authenticatie(request_body.code, request_body.redirect_uri)
    request.session["user_id"] = user_id
    return {"user_id": user_id}


@auth_router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return {"message": "Logged out"}


@auth_router.get("/google/profile")
async def google_profile(user_id: int = Depends(get_user_id_from_session)):
    return await auth_service.get_google_profile(user_id)


@auth_router.get("/google/callback")
async def google_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Code parameter is required.")
    return {"code": code}
