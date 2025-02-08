import openai
from googleapiclient.errors import HttpError

from agents.classify_single_mail import classify_single_mail
from agents.embedding.cluster_mails import cluster_mails
from agents.summary.make_report import make_report
from agents.summary_single_mail import summary_single_mail
from gmail_api.gmail_service import GmailService
from gmail_api.mail import Mail
from utils import convert_mail_dict_to_df
from utils.checklist_builder import build_json_checklist
from utils.configuration import Config


def pipeline(gmail_service: GmailService, api_key: str):
    try:
        mail_dict: dict[str, Mail] = gmail_service.fetch_mails()

        summary_single_mail(mail_dict, api_key)
        classify_single_mail(mail_dict, Config.config, api_key)

        cluster_mails(mail_dict, Config.config)

        report = make_report(mail_dict, api_key, Config.config)

        df = convert_mail_dict_to_df(mail_dict)

        json_checklist = build_json_checklist(df)

        return json_checklist, report

    except HttpError as error:
        print(f"An error occurred: {error}")
    except openai.RateLimitError as rate_err:
        print("[RateLimitError] API 한도가 초과되었습니다. 현재까지의 토큰 사용량만 보고합니다.")
        print(f"에러 메세지: {rate_err}")
