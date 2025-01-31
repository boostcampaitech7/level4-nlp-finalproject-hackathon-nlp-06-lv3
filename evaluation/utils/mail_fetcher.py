from datetime import datetime

from tqdm import tqdm

from gmail_api import GmailService, Mail


def fetch_emails(gmail_service: GmailService, date: str, n: int):
    """Gmail API를 사용하여 지정된 날짜의 이메일을 가져오는 함수."""
    messages = gmail_service.get_today_n_messages(date, n)
    mail_dict: dict[str, Mail] = {}
    for idx, message_metadata in enumerate(tqdm(messages, desc="Processing Emails")):
        mail_id = f"{datetime.now().strftime('%Y/%m/%d')}/{len(messages)-idx:04d}"
        mail = Mail(message_metadata["id"], mail_id, gmail_service)
        mail_dict[mail_id] = mail

    return mail_dict
