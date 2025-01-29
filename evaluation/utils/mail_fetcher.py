from tqdm import tqdm

from gmail_api import Mail, MessageHandler


def fetch_emails(gmail_service, date, n):
    """Gmail API를 사용하여 지정된 날짜의 이메일을 가져오는 함수."""
    messages = gmail_service.get_today_n_messages(date, n)
    mail_dict = {}

    for message_metadata in tqdm(messages, desc="이메일 데이터 가져오는 중"):
        message_id = message_metadata["id"]
        message = gmail_service.get_message_details(message_id)
        body, attachments = MessageHandler.process_message(gmail_service.service, message)
        headers = MessageHandler.process_headers(message)

        mail_dict[message_id] = Mail(
            message_id,
            headers["sender"],
            [headers["recipients"]],
            headers["subject"],
            body,
            [headers["cc"]],
            attachments,
            headers["date"],
        )

    return mail_dict
