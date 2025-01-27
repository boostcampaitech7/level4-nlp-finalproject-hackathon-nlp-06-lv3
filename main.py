# from datetime import datetime, timedelta

from dotenv import load_dotenv
from googleapiclient.errors import HttpError
from tqdm import tqdm

from agents import ClassificationAgent, SelfRefineAgent, SummaryAgent, map_category
from gmail_api import GmailService, Mail


def main():
    load_dotenv()

    try:
        gmail_service = GmailService()

        # Fetch last N messages
        yesterday = "2025/01/10"  # (datetime.today() - timedelta(days=1)).strftime("%Y/%m/%d")
        n = 10

        messages = gmail_service.get_today_n_messages(yesterday, n)
        mail_dict: dict[str, Mail] = {}
        for message_metadata in tqdm(messages, desc="Processing Emails"):
            message_id = message_metadata["id"]
            mail = Mail(message_id, gmail_service)

            # 룰베이스 분류
            if "(광고)" not in mail.subject:
                mail_dict[message_id] = mail

        # 개별 메일 요약, 분류
        summay_agent = SummaryAgent("solar-pro", "single")
        classification_agent = ClassificationAgent("solar-pro")

        for mail_id, mail in mail_dict.items():
            summary = summay_agent.process(mail)
            category = classification_agent.process(mail)
            mail_dict[mail_id].summary = summary["summary"]
            mail_dict[mail_id].label = category

            print(category)
            print(summary)
            print("=" * 40)

        report_agent = SummaryAgent("solar-pro", "final")
        self_refine_agent = SelfRefineAgent("solar-pro", "final")

        report: dict = self_refine_agent.process(mail_dict, report_agent, 10)

        print("=============FINAL_REPORT================")
        for label, mail_reports in report.items():
            print(map_category(label))
            for mail_report in mail_reports:
                mail_subject = mail_dict[mail_report["mail_id"]].subject
                print(f"메일 subject: {mail_subject}")
                print(f"리포트: {mail_report['report']}")
            print()

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
