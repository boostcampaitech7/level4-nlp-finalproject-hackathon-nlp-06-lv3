import os
import webbrowser

from dotenv import load_dotenv

load_dotenv()

# OAuth Parameters
scopes = [
    "openid",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]
access_type = "offline"
response_type = "code"
state = "state_parameter_passthrough_value"
redirect_uri = "http://localhost:8000/auth/google/callback"

# Generate OAuth URL
URL = (
    "https://accounts.google.com/o/oauth2/v2/auth"
    f"?scope={' '.join(scopes)}&"
    f"access_type={access_type}&"
    f"prompt=consent&"
    f"response_type={response_type}&"
    f"state={state}&"
    f"redirect_uri={redirect_uri}&"
    f"client_id={os.getenv('GOOGLE_CLIENT_ID')}"
)
URL = URL.replace(" ", "%20")

print(f"Open this URL in your browser: {URL}")


webbrowser.open(URL)
