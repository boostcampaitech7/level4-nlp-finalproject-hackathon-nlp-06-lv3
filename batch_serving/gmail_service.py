from collections import deque

from tqdm import tqdm

from batch_serving.mail import Mail
from batch_serving.other_utils.other_utils import (
    decode_base64,
    delete_file,
    parse_document,
    replace_image_pattern_with,
    replace_url_pattern_from,
    save_file,
)
from utils.configuration import Config


class GmailService:
    def __init__(self, service):
        self.service = service

    def list_messages(self, max_results=5):
        if not self.service:
            print("[Error] GmailService: 인증 실패 또는 service가 None입니다.")
            return []

        results = self.service.users().messages().list(userId="me", maxResults=max_results).execute()
        return results.get("messages", [])

    def fetch_mails(self):
        start_date = Config.config["gmail"]["start_date"]
        end_date = Config.config["gmail"]["end_date"]
        n = Config.config["gmail"]["max_mails"]

        messages = self.get_today_n_messages(start_date, n)
        mail_dict = {}
        for idx, msg_meta in enumerate(tqdm(messages, desc="Processing Emails")):
            mail_id = f"{end_date}/{len(messages)-idx:04d}"
            message = self.get_message_details(msg_meta["id"])
            body, attachments = self.process_message(message)
            headers = self.process_headers(message)
            mail = Mail(msg_meta["id"], mail_id, body, attachments, headers)
            # 예시로 (광고) 필터만 적용
            if "(광고)" not in mail.subject:
                mail_dict[msg_meta["id"]] = mail
        return mail_dict

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

    def process_attachment(self, message_id, part, files, save_dir="downloaded_files"):
        att_id = part["body"]["attachmentId"]
        att = self.service.users().messages().attachments().get(userId="me", messageId=message_id, id=att_id).execute()
        saved_file_path = save_file(decode_base64(att["data"]), part["filename"], save_dir=save_dir)
        if saved_file_path:  # 파일이 정상적으로 저장된 경우
            files.append(parse_document(saved_file_path))
            delete_file(saved_file_path)
        return files

    def process_message_part(self, message_id: str, part: dict, files: deque = None):
        if files is None:
            files = deque()

        mime_type = part["mimeType"]
        body_data = part.get("body", {}).get("data")

        if mime_type == "text/plain" and body_data:
            decoded_bytes = decode_base64(body_data)
            return decoded_bytes.decode("utf-8", errors="replace"), files

        if part.get("filename"):  # 첨부파일 처리
            files = self.process_attachment(message_id, part, files)
            return "", files

        # multipart
        plain_text = ""
        if "multipart" in mime_type:
            for sub_part in part.get("parts", []):
                text, files = self.process_message_part(message_id, sub_part, files)
                plain_text += text

        return plain_text, files

    def process_message(self, message):
        payload = message.get("payload", {})
        body, filenames = self.process_message_part(message["id"], payload)  # 임시, 아래에서 재호출에 주의

        # 여기서는 그냥 body, filenames만 리턴하도록 예시
        replaced_body, attachments = replace_image_pattern_with(body, filenames)
        replaced_body = replace_url_pattern_from(replaced_body)
        return replaced_body, attachments

    def process_headers(self, message):
        payload = message.get("payload", {})
        headers = payload.get("headers", [])
        return {
            "recipients": next((item["value"] for item in headers if item["name"] == "To"), None),
            "sender": next((item["value"] for item in headers if item["name"] == "From"), None),
            "cc": next((item["value"] for item in headers if item["name"] == "Cc"), ""),
            "subject": next((item["value"] for item in headers if item["name"] == "Subject"), None),
            "date": next((item["value"] for item in headers if item["name"] == "Date"), None),
        }
