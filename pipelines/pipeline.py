import openai
from googleapiclient.errors import HttpError

from gmail_api.gmail_service import GmailService
from gmail_api.mail import Mail
from pipelines.checklist_builder import build_json_checklist
from pipelines.classify_single_mail import classify_single_mail
from pipelines.cluster_mails import cluster_mails
from pipelines.make_report import make_report
from pipelines.summary_single_mail import summary_single_mail


def pipeline(gmail_service: GmailService):
    try:
        mail_dict: dict[str, Mail] = gmail_service.fetch_mails()

        summary_single_mail(mail_dict)
        classify_single_mail(mail_dict)

        cluster_mails(mail_dict)

        report = make_report(mail_dict)

        json_checklist = build_json_checklist(mail_dict)
        print(json_checklist)

        return json_checklist, report

    except HttpError as error:
        print(f"An error occurred: {error}")
    except openai.RateLimitError as rate_err:
        print("[RateLimitError] API 한도가 초과되었습니다. 현재까지의 토큰 사용량만 보고합니다.")
        print(f"에러 메세지: {rate_err}")
