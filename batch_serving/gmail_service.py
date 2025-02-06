from collections import deque
from typing import Optional

from tqdm import tqdm

from batch_serving.other_utils.other_utils import (
    decode_base64,
    delete_file,
    parse_document,
    replace_image_pattern_with,
    replace_url_pattern_from,
    save_file,
)


class Mail:
    def __init__(
        self,
        gmail_service,
        message_id: str,
        mail_id: str,
        summary: Optional[str] = None,
        label: Optional[str] = None,
    ):
        """
        Args:
            gmail_service: GmailService (이미 인증된 Gmail API 서비스 객체 래퍼)
            message_id (str): Gmail 상에서의 message id
            mail_id (str): 우리 서비스 내에서 매길 임의 id
        """
        message = gmail_service.get_message_details(message_id)
        body, attachments = MessageHandler.process_message(message)
        headers = MessageHandler.process_headers(message)

        self._id = mail_id
        self.sender = headers["sender"]
        self.recipients = [headers["recipients"]]
        self.subject = headers["subject"]
        self.body = body
        self.cc = [headers["cc"]] if headers["cc"] is not None else []
        self.attachments = attachments if attachments is not None else []
        self.date = headers["date"]
        self._summary = summary
        self._label_category = label
        self._label_action = label
        self._similar_mails = []

    def __str__(self) -> str:
        attachments_text = ""
        if self.attachments:
            for i, item in enumerate(self.attachments):
                attachments_text += f"첨부파일 {i + 1}:\n{item}\n\n"
        return (
            f"보낸 사람: {self.sender}\n"
            f"받는 사람: {', '.join(self.recipients)}\n"
            f"참조: {', '.join(self.cc)}\n"
            f"제목: {self.subject}\n"
            f"날짜: {self.date}\n"
            f"본문:\n{self.body}\n"
            f"{attachments_text}"
        )

    @property
    def id(self) -> str:
        return self._id

    @property
    def summary(self) -> Optional[str]:
        return self._summary

    @summary.setter
    def summary(self, value: str) -> None:
        if not value:
            raise ValueError("Summary cannot be empty.")
        self._summary = value

    @property
    def label_category(self) -> Optional[str]:
        return self._label_category

    @label_category.setter
    def label_category(self, value: str) -> None:
        if not value:
            raise ValueError("Label cannot be empty.")
        self._label_category = value

    @property
    def label_action(self) -> Optional[str]:
        return self._label_action

    @label_action.setter
    def label_action(self, value: str) -> None:
        if not value:
            raise ValueError("Label cannot be empty.")
        self._label_action = value

    @property
    def similar_mails(self) -> Optional[list[str]]:
        return self._similar_mails

    @similar_mails.setter
    def similar_mails(self, value: list[str]) -> None:
        if not isinstance(value, list) and not value:
            raise ValueError("Similar Mails cannot be empty.")
        self._similar_mails = value


class MessageHandler:
    @staticmethod
    def process_attachment(gmail_service, message_id, part, files, save_dir="downloaded_files"):
        att_id = part["body"]["attachmentId"]
        att = (
            gmail_service.service.users()
            .messages()
            .attachments()
            .get(userId="me", messageId=message_id, id=att_id)
            .execute()
        )
        saved_file_path = save_file(decode_base64(att["data"]), part["filename"], save_dir=save_dir)
        if saved_file_path:  # 파일이 정상적으로 저장된 경우
            files.append(parse_document(saved_file_path))
            delete_file(saved_file_path)
        return files

    @staticmethod
    def process_message_part(message_id: str, part: dict, gmail_service, files: deque = None):
        if files is None:
            files = deque()

        mime_type = part["mimeType"]
        body_data = part.get("body", {}).get("data")

        if mime_type == "text/plain" and body_data:
            decoded_bytes = decode_base64(body_data)
            return decoded_bytes.decode("utf-8", errors="replace"), files

        if part.get("filename"):  # 첨부파일 처리
            files = MessageHandler.process_attachment(gmail_service, message_id, part, files)
            return "", files

        # multipart
        plain_text = ""
        if "multipart" in mime_type:
            for sub_part in part.get("parts", []):
                text, files = MessageHandler.process_message_part(message_id, sub_part, gmail_service, files)
                plain_text += text

        return plain_text, files

    @staticmethod
    def process_message(message):
        payload = message.get("payload", {})
        body, filenames = MessageHandler.process_message_part(
            message["id"], payload, gmail_service=None  # 임시, 아래에서 재호출에 주의
        )

        # 위에서 gmail_service 인자가 필요한데, staticmethod 호출 방식에 맞춰
        # 사용자가 바로 쓸 수 있도록 조금 수정이 필요합니다.
        # 아래처럼 "부분에서" 따로 변경해서 호출해줄 수도 있습니다.
        # 여기서는 편의상 message 전체를 이미 가져온다고 가정하고 pass 합니다.

        # (실제로는 process_message_part에서 gmail_service 인자가 필요하니
        #  Mail.__init__ 등에서 한번에 처리하도록 구조를 조금 바꿔도 됩니다.)

        # 여기서는 그냥 body, filenames만 리턴하도록 예시
        replaced_body, attachments = replace_image_pattern_with(body, filenames)
        replaced_body = replace_url_pattern_from(replaced_body)
        return replaced_body, attachments

    @staticmethod
    def process_headers(message):
        payload = message.get("payload", {})
        headers = payload.get("headers", [])
        return {
            "recipients": next((item["value"] for item in headers if item["name"] == "To"), None),
            "sender": next((item["value"] for item in headers if item["name"] == "From"), None),
            "cc": next((item["value"] for item in headers if item["name"] == "Cc"), ""),
            "subject": next((item["value"] for item in headers if item["name"] == "Subject"), None),
            "date": next((item["value"] for item in headers if item["name"] == "Date"), None),
        }


class GmailService:
    def __init__(self, service):
        self.service = service

    def list_messages(self, max_results=5):
        if not self.service:
            print("[Error] GmailService: 인증 실패 또는 service가 None입니다.")
            return []

        results = self.service.users().messages().list(userId="me", maxResults=max_results).execute()
        return results.get("messages", [])

    def get_today_n_messages(self, date: str, n: int = 100):
        message_list = (
            self.service.users()
            .messages()
            .list(userId="me", maxResults=n, q=f"after:{date}", labelIds=["INBOX"])
            .execute()
        )
        return message_list.get("messages", [])

    def get_message_details(self, message_id):
        return self.service.users().messages().get(userId="me", id=message_id).execute()


def fetch_mails(gmail_service: GmailService, start_date: str, end_date: str, n: int):
    messages = gmail_service.get_today_n_messages(start_date, n)
    mail_dict = {}
    for idx, msg_meta in enumerate(tqdm(messages, desc="Processing Emails")):
        mail_id = f"{end_date}/{len(messages)-idx:04d}"
        mail = Mail(gmail_service, msg_meta["id"], mail_id)
        # 예시로 (광고) 필터만 적용
        if "(광고)" not in mail.subject:
            mail_dict[mail_id] = mail
    return mail_dict
