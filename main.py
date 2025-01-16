import os
from datetime import datetime

import dotenv
from googleapiclient.errors import HttpError
from langchain_upstage import ChatUpstage

from gmail_api import GmailService, Mail, MessageHandler
from summary import summarize


def main():
    # 초기 환경 설정
    dotenv.load_dotenv()

    try:
        gmail_service = GmailService()

        # Fetch last N messages
        today_date = datetime.today().strftime("%Y/%m/%d")
        n = 100
        messages = gmail_service.get_today_n_messages(today_date, n)
        mail_list = []
        for message_metadata in messages:
            message_id = message_metadata["id"]
            message = gmail_service.get_message_details(message_id)
            body = MessageHandler.process_message(gmail_service.service, message)
            headers = MessageHandler.process_headers(message)

            mail = Mail(
                headers["sender"], [headers["recipients"]], headers["subject"], body, [headers["cc"]], headers["date"]
            )
            mail_list.append(mail)

        chat = ChatUpstage(api_key=os.getenv("UPSTAGE_API_KEY"), model="solar-pro")
        summary_list = []
        for idx, mail in enumerate(mail_list):
            summary = summarize(chat, mail, "summary")
            summary_list.append(summary)

            print(mail)
            print(summary)
            print("=" * 40)

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
