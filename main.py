# from datetime import datetime, timedelta

from dotenv import load_dotenv
from googleapiclient.errors import HttpError

from agents import SelfRefineAgent, SummaryAgent
from gmail_api import GmailService, Mail, MessageHandler


def main():
    load_dotenv()

    try:
        gmail_service = GmailService()

        # Fetch last N messages
        yesterday = "2025/01/10"  # (datetime.today() - timedelta(days=1)).strftime("%Y/%m/%d")
        n = 10

        messages = gmail_service.get_today_n_messages(yesterday, n)
        mail_dict: dict[str, Mail] = {}
        for message_metadata in messages:
            message_id = message_metadata["id"]
            message = gmail_service.get_message_details(message_id)
            body, attachments = MessageHandler.process_message(gmail_service.service, message)
            headers = MessageHandler.process_headers(message)

            mail = Mail(
                message_id,
                headers["sender"],
                [headers["recipients"]],
                headers["subject"],
                body,
                [headers["cc"]],
                attachments,
                headers["date"],
            )
            # 룰베이스 분류
            if "(광고)" not in mail.subject:
                mail_dict[message_id] = mail

        # 개별 메일 요약, 분류
        summay_agent = SummaryAgent("solar-pro", "single")
        classification_agent = SummaryAgent("solar-pro", "classification")

        for mail_id, mail in mail_dict.items():
            summary = summay_agent.process(mail)
            category = classification_agent.process(mail)
            mail_dict[mail_id].summary = summary
            mail_dict[mail_id].label = category

            # print(mail)
            # print(summary)
            # print(category)
            # print("=" * 40)

        report_agent = SummaryAgent("solar-pro", "final")
        self_refine_agent = SelfRefineAgent("solar-pro", "final")

        report = self_refine_agent.process(mail_dict, report_agent)
        print("=============FINAL_REPORT================")
        print(report)

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
