import os

import requests
from fastapi import HTTPException
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

# Google OAuth2 setup
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:3000"


def google_authenticatie(code: str):
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

        flow.fetch_token(code=code)

        credentials = flow.credentials
        print(credentials)
        tokens = {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "expires_in": credentials.expiry,
        }
        print(tokens)

        return tokens
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")


def get_token_info(access_token: str):
    try:
        response = requests.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"access_token": access_token},
        )
        response.raise_for_status()
        return response.json()  # Return token information
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=400, detail="Invalid token")


def refresh_access_token(refresh_token: str):
    try:
        credentials = Credentials(
            None,
            refresh_token=refresh_token,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            token_uri="https://oauth2.googleapis.com/token",
        )
        credentials.refresh(Request())

        new_tokens = {"access_token": credentials.token, "expires_in": credentials.expiry}

        return new_tokens
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Token refresh failed: {str(e)}")


def get_google_profile(access_token: str):
    try:
        response = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        return response.json()  # Return user profile information
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=400, detail="Invalid token")
