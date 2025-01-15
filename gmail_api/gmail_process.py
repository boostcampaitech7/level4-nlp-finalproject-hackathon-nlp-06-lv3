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

    def get_user_profile(self):
        """
        Retrieves the user's Gmail profile information.
        Returns:
            profile (dict): User profile details.
        """
        profile = self.service.users().getProfile(userId="me").execute()
        return profile

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

    def get_threads_from_last_n_messages(self, n):
        """
        Fetches threads from the list of last N messages.

        Args:
            n (int): Number of messages to fetch

        Returns:
            threads (set): Set of threads
        """
        message_list = self.get_last_n_messages(n)
        return set(message["threadId"] for message in message_list["messages"])


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
    def save_attachment(service, message_id, part, save_dir="Downloaded_files"):
        """
        Saves an attachment from a message part to the local file system.
        Args:
            service: Gmail API service object.
            message_id (str): ID of the Gmail message.
            part (dict): Message part containing the attachment.
            save_dir (str): Directory to save attachments.
        """
        att_id = part["body"]["attachmentId"]
        att = service.users().messages().attachments().get(userId="me", messageId=message_id, id=att_id).execute()
        data = att["data"].replace("-", "+").replace("_", "/")
        file_data = base64.urlsafe_b64decode(data.encode("UTF-8"))

        os.makedirs(save_dir, exist_ok=True)
        filepath = os.path.join(save_dir, part["filename"])

        with open(filepath, "wb") as file:
            file.write(file_data)
        print(f"Attachment saved: {filepath}")

    @staticmethod
    def process_message_part(service, message_id, part):
        """
        Recursively processes a MessagePart, decoding bodies and saving attachments.
        Args:
            service: Gmail API service object.
            message_id (str): ID of the Gmail message.
            part (dict): Message part.
        """
        # Decode and print the body if it exists
        if "body" in part and "data" in part["body"]:
            decoded_data = MessageHandler.decode_message_part(part["body"]["data"])
            # TODO: 파일 저장 로직 추가하기
            print(f"Decoded body: {decoded_data}")

        # Save the attachment if the part contains a filename
        if part.get("filename"):
            MessageHandler.save_attachment(service, message_id, part)

        # Recursively process sub-parts
        if "parts" in part:
            for sub_part in part["parts"]:
                MessageHandler.process_message_part(service, message_id, sub_part)

    @staticmethod
    def process_message(service, message):
        """
        Processes a single message, including decoding and saving attachments.
        Args:
            service: Gmail API service object.
            message (dict): Full message details.
        """
        print(f"Message ID: {message['id']}")
        print(f"Snippet: {message['snippet']}")
        print(f"Labels: {message.get('labelIds', [])}")

        payload = message.get("payload", {})
        MessageHandler.process_message_part(service, message["id"], payload)


def main():
    try:
        gmail_service = GmailService()

        # Fetch user profile
        profile = gmail_service.get_user_profile()
        print("User Profile:", profile)

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
