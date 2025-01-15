import base64
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class GmailService:
    def __init__(self):
        self.service = self._authenticate_with_token()

    @staticmethod
    def _authenticate_with_token():
        """
        Authenticates the user using token.json or performs OAuth2 flow if necessary.
        Returns:
            service (Resource): Gmail API service object.
        """
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port=8080, prompt="consent", access_type="offline")

            with open("token.json", "w") as token:
                token.write(creds.to_json())

        return build("gmail", "v1", credentials=creds)

    def get_last_n_messages(self, n):
        """
        Fetches the list of last N messages.
        Args:
            n (int): Number of messages to fetch.
        Returns:
            messages (list): List of message metadata.
        """
        message_list = self.service.users().messages().list(userId="me", maxResults=n).execute()
        return message_list.get("messages", [])

    def get_message_details(self, message_id):
        """
        Fetches details of a single message by ID.
        Args:
            message_id (str): ID of the Gmail message.
        Returns:
            message (dict): Full message details.
        """
        return self.service.users().messages().get(userId="me", id=message_id).execute()


class MessageHandler:
    @staticmethod
    def decode_message_part(data):
        """
        Decodes a base64-encoded message part.
        Args:
            data (str): Base64-encoded string.
        Returns:
            str: Decoded string.
        """
        data = data.replace("-", "+").replace("_", "/")
        decoded_data = base64.b64decode(data)
        return str(decoded_data, encoding="utf-8")

    @staticmethod
    def process_message_part(service, message_id: str, part: dict) -> str:
        """
        Recursively processes a MessagePart, decoding bodies.
        Only consider MIME type: text/plain
        Args:
            service: Gmail API service object.
            message_id (str): ID of the Gmail message.
            part (dict): Message part.
        Returns:
            str: Plain text of message.
        """
        # TODO: 다양한 MIME type에 대한 처리

        if part["mimeType"] == "text/plain":
            decoded_data = MessageHandler.decode_message_part(part["body"]["data"])
            return decoded_data

        plain_text = ""
        if "multipart" in part["mimeType"]:
            for sub_part in part["parts"]:
                plain_text += MessageHandler.process_message_part(service, message_id, sub_part)

        return plain_text

    @staticmethod
    def process_message(service, message):
        """
        Processes a single message, including decoding.
        Args:
            service: Gmail API service object.
            message (dict): Full message details.
        """
        print(f"Message ID: {message['id']}")
        print(f"Snippet: {message['snippet']}")
        print(f"Labels: {message.get('labelIds', [])}")

        payload = message.get("payload", {})
        print(MessageHandler.process_message_part(service, message["id"], payload))


def main():
    try:
        gmail_service = GmailService()

        # Fetch last N messages
        n = 1
        messages = gmail_service.get_last_n_messages(n)

        for message_metadata in messages:
            message_id = message_metadata["id"]
            message = gmail_service.get_message_details(message_id)
            MessageHandler.process_message(gmail_service.service, message)

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
