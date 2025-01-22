# from datetime import datetime, timedelta

from dotenv import load_dotenv
from googleapiclient.errors import HttpError

from agents import SelfRefineAgent, SummaryAgent
from gmail_api import GmailService, Mail, MessageHandler


def main():
    load_dotenv()
    try:
        load_dotenv()
        gmail_service = GmailService()

        # Fetch last N messages
        yesterday = "2025/01/20"  # (datetime.today() - timedelta(days=1)).strftime("%Y/%m/%d")
        n = 1

        messages = gmail_service.get_today_n_messages(yesterday, n)
        mail_list = []
        for message_metadata in messages:
            message_id = message_metadata["id"]
            message = gmail_service.get_message_details(message_id)
            body, attachments = MessageHandler.process_message(gmail_service.service, message)
            headers = MessageHandler.process_headers(message)

            mail = Mail(
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
                mail_list.append(mail)

        # 개별 메일 요약, 분류
        summay_agent = SummaryAgent("solar-pro", "single")
        classification_agent = SummaryAgent("solar-pro", "classification")

        result_list = []

        for mail in mail_list:
            summary = summay_agent.process(mail)
            category = classification_agent.process(mail)
            result_list.append({"mail": mail, "summary": summary, "category": category})

            # print(mail)
            # print(summary)
            # print(category)
            # print("=" * 40)

        report_agent = SummaryAgent("solar-pro", "final")
        self_refine_agent = SelfRefineAgent("solar-pro", "final")

        report = self_refine_agent.process(result_list, report_agent)
        print("=============FINAL_REPORT================")
        print(report)

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
