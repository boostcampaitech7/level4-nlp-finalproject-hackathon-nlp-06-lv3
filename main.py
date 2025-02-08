import os

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from h11 import Request

from agents.pipeline import pipeline
from batch_serving import GmailService
from batch_serving.db_utils import SCOPES


def create_service():
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=8080, prompt="consent", access_type="offline")

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    with open("token.json", "w") as token:
        token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def main():
    load_dotenv()

    # TODO: config 대체
    gmail_service = GmailService(create_service())

    _, report = pipeline(gmail_service, os.getenv("UPSTAGE_API_KEY"))

    print("============ FINAL REPORT=============")
    print(report)
    print("=======================================================")


if __name__ == "__main__":
    main()
