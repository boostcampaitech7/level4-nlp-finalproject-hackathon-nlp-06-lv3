import os
from datetime import datetime, timezone

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

from server._core.errors.exceptions.custom_exception import CustomException
from server._core.errors.exceptions.error_code import ErrorCode
from server.database.connection import database
from server.models.user import User
from server.schemas import auth_request, auth_response

# Google OAuth2 setup
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")


def is_login(user_id):
    return auth_response.IsLoginDto(user_id)


async def google_authenticatie(request_dto: auth_request.GoogleAuthDto):
    try:
        # Initialize the Google OAuth2 Flow
        flow = Flow.from_client_secrets_file(
            "credentials.json",  # Ensure you have this file from Google Cloud Console
            scopes=[
                "openid",
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
            ],
            redirect_uri=request_dto.redirect_uri,
        )

        flow.fetch_token(code=request_dto.code)

        token_info = get_token_info(flow.credentials.token)  # Validate the access token
        user = await database.fetch_one(
            "SELECT * FROM user_tb WHERE google_id = :google_id", {"google_id": token_info["sub"]}
        )
        if not user:
            user_id = await database.execute(
                (
                    "INSERT INTO user_tb (google_id, access_token, refresh_token, expiry) "
                    "VALUES (:google_id, :access_token, :refresh_token, :expiry)"
                ),
                {
                    "google_id": token_info["sub"],
                    "access_token": flow.credentials.token,
                    "refresh_token": flow.credentials.refresh_token,
                    "expiry": flow.credentials.expiry,
                },
            )
        else:
            user_id = user["id"]
            await database.execute(
                (
                    "UPDATE user_tb SET access_token = :access_token, refresh_token = :refresh_token, expiry = :expiry "
                    "WHERE google_id = :google_id"
                ),
                {
                    "google_id": token_info["sub"],
                    "access_token": flow.credentials.token,
                    "refresh_token": flow.credentials.refresh_token,
                    "expiry": flow.credentials.expiry,
                },
            )
        return auth_response.GoogleAuthDto(user_id=user_id), user_id

    except Exception:
        raise CustomException(ErrorCode.LOGIN_FAILED)


def get_token_info(access_token: str):
    try:
        response = requests.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"access_token": access_token},
        )
        response.raise_for_status()
        return response.json()  # Return token information
    except requests.exceptions.RequestException:
        raise CustomException(ErrorCode.INVALID_TOKEN)


async def get_google_profile(user: User):
    if is_expired(user["expiry"]):
        new_tokens = await refresh_access_token(user.id, user["refresh_token"])
        access_token = new_tokens
    else:
        access_token = user["access_token"]

    response = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    response.raise_for_status()
    return auth_response.GoogleProfileDto(response.json())


def is_expired(expiry_time: datetime):
    expiry_time = expiry_time.replace(tzinfo=timezone.utc)
    utc_current_time = datetime.now(timezone.utc)
    return utc_current_time >= expiry_time  # 만료 시간과 현재 시간을 비교


async def refresh_access_token(user_id: int, refresh_token: str) -> str:
    try:
        credentials = Credentials(
            None,
            refresh_token=refresh_token,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            token_uri="https://oauth2.googleapis.com/token",
        )
        credentials.refresh(Request())

        await database.execute(
            ("UPDATE user_tb SET access_token = :access_token, expiry = :expiry WHERE id = :user_id"),
            {
                "user_id": user_id,
                "access_token": credentials.token,
                "expiry": credentials.expiry,
            },
        )

        return credentials.token
    except Exception as e:
        raise CustomException(ErrorCode.SERVER_ERROR, f"Token refresh failed: {str(e)}")


def google_callback(code: str):
    return auth_response.GoogleCallbackDto(code=code)
