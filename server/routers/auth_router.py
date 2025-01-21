import os

import requests
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from pydantic import BaseModel

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
async def google_auth(request: GoogleAuthRequest):
    try:
        # Initialize the Google OAuth2 Flow
        flow = Flow.from_client_secrets_file(
            "client_secrets.json",  # Ensure you have this file from Google Cloud Console
            scopes=[
                "openid",
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
            ],
            redirect_uri=REDIRECT_URI,
        )

        flow.fetch_token(code=request.code)

        credentials = flow.credentials
        tokens = {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "expires_in": credentials.expiry,
        }

        return tokens
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")


class ValidateTokenRequest(BaseModel):
    access_token: str


@auth_router.post("/google/validate-token")
async def validate_token(request_body: ValidateTokenRequest):
    try:
        response = requests.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"access_token": request_body.access_token},
        )
        response.raise_for_status()
        return response.json()  # Return token information
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=400, detail="Invalid token")


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@auth_router.post("/google/refresh-token")
async def refresh_google_token(request: RefreshTokenRequest):
    try:
        credentials = Credentials(
            None,
            refresh_token=request.refresh_token,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            token_uri="https://oauth2.googleapis.com/token",
        )
        credentials.refresh(Request())

        new_tokens = {"access_token": credentials.token, "expires_in": credentials.expiry}

        return new_tokens
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Token refresh failed: {str(e)}")


class ProfileRequest(BaseModel):
    access_token: str


@auth_router.get("/google/profile")
async def get_google_profile(request: ProfileRequest):
    try:
        response = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers={"Authorization": f"Bearer {request.access_token}"},
        )
        response.raise_for_status()
        return response.json()  # Return user profile information
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=400, detail="Invalid token")
