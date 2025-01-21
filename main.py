# from datetime import datetime

from googleapiclient.errors import HttpError

from agents import SummaryAgent
from gmail_api import GmailService, Mail, MessageHandler


def main():
    try:
        gmail_service = GmailService()

        # Fetch last N messages
        today_date = "2025/01/14"  # datetime.today().strftime("%Y/%m/%d")
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
            # 룰베이스 분류
            if "(광고)" not in mail.subject:
                mail_list.append(mail)

        # 개별 메일 요약, 분류
        summay_agent = SummaryAgent("single")
        classification_agent = SummaryAgent("classification")
        summary_list = []
        category_list = []

        for mail in mail_list:
            summary = summay_agent.process(mail)
            summary_list.append(summary)
            category = classification_agent.summarize(mail)
            category_list.append(category)

            print(mail)
            print(summary)
            print(category)
            print("=" * 40)

        report_agent = SummaryAgent("final")
        report = report_agent.process(summary_list)

        print("=============FINAL_REPORT================")
        print(report)
    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
