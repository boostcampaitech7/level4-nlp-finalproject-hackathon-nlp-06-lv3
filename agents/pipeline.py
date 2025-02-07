import openai
from dotenv import load_dotenv
from googleapiclient.errors import HttpError

from agents import EmbeddingManager, ReflexionFramework, SummaryAgent
from agents.classify_single_mail import classify_single_mail
from agents.summary_single_mail import summary_single_mail
from batch_serving import GmailService, Mail
from checklist_builder import build_json_checklist
from utils import convert_mail_dict_to_df, load_config


def cluster_mails(mail_dict: dict[str, Mail], config: dict):
    embedding_manager = EmbeddingManager(
        embedding_model_name=config["embedding"]["model_name"],
        similarity_metric=config["embedding"]["similarity_metric"],
        similarity_threshold=config["embedding"]["similarity_threshold"],
        is_save_results=config["embedding"]["save_results"],
    )
    embedding_manager.run(mail_dict)


def make_report(mail_dict: dict[str, Mail], api_key: str, config: dict):
    summary_agent = SummaryAgent(
        model_name="solar-pro",
        summary_type="final",
        api_key=api_key,
        temperature=config["temperature"]["summary"],
        seed=config["seed"],
    )

    origin_mail = ""
    for _, mail in mail_dict.items():
        origin_mail += mail.summary + "\n"

    self_reflection_agent = ReflexionFramework("solar_pro", "final", config)

    reflexion_summary, token_usage = self_reflection_agent.process(origin_mail, summary_agent)

    return reflexion_summary


def pipeline(gmail_service: GmailService, api_key: str):
    load_dotenv()

    # YAML 파일 로드
    config = load_config()

    try:
        mail_dict: dict[str, Mail] = gmail_service.fetch_mails(
            start_date=config["gmail"]["start_date"],
            end_date=config["gmail"]["end_date"],
            n=config["gmail"]["max_mails"],
        )

        summary_single_mail(mail_dict, config, api_key)
        classify_single_mail(mail_dict, config, api_key)

        cluster_mails(mail_dict, config)

        report = make_report(mail_dict, api_key, config)

        df = convert_mail_dict_to_df(mail_dict)

        json_checklist = build_json_checklist(df)

        return json_checklist, report

    except HttpError as error:
        print(f"An error occurred: {error}")
    except openai.RateLimitError as rate_err:
        print("[RateLimitError] API 한도가 초과되었습니다. 현재까지의 토큰 사용량만 보고합니다.")
        print(f"에러 메세지: {rate_err}")
