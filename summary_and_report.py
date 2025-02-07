import openai
from dotenv import load_dotenv
from googleapiclient.errors import HttpError

from agents import (
    ClassificationAgent,
    ClassificationType,
    EmbeddingManager,
    ReflexionFramework,
    SelfRefineAgent,
    SummaryAgent,
)
from batch_serving import GmailService, Mail, fetch_mails
from checklist_builder import build_json_checklist
from evaluation import ClassificationEvaluationAgent, print_evaluation_results, summary_evaluation_data
from evaluator import evaluate_summary
from utils import TokenManager, convert_mail_dict_to_df, load_config, run_with_retry


def summary_and_classify(mail_dict: dict[str, Mail], config: dict, api_key):
    temperature: int = config["temperature"]["summary"]
    seed: int = config["seed"]
    do_class_eval: bool = config["evaluation"]["classification_eval"]
    do_sum_eval: bool = config["evaluation"]["summary_eval"]

    summary_agent = SummaryAgent("solar-pro", "single", api_key, temperature, seed)
    self_refine_agent = SelfRefineAgent("solar-pro", "single", api_key, temperature, seed)
    classification_agent = ClassificationAgent("solar-pro", api_key, temperature, seed)
    if do_class_eval:
        class_eval_agent = ClassificationEvaluationAgent(
            model="gpt-4o",
            human_evaluation=config["classification"]["do_manual_filter"],
            inference=config["classification"]["inference"],
        )

    for mail_id, mail in mail_dict.items():
        summary, token_usage = run_with_retry(self_refine_agent.process, mail, summary_agent)
        mail_dict[mail_id].summary = summary
        TokenManager.total_token_usage += token_usage

        if do_class_eval:
            category = run_with_retry(class_eval_agent.process, mail, classification_agent, ClassificationType.CATEGORY)
            action = run_with_retry(class_eval_agent.process, mail, classification_agent, ClassificationType.ACTION)
        else:
            category = run_with_retry(classification_agent.process, mail, ClassificationType.CATEGORY)
            action = run_with_retry(classification_agent.process, mail, ClassificationType.ACTION)
        mail_dict[mail_id].label_category = category
        mail_dict[mail_id].label_action = action

        print(f"{mail_id}\ncategory label: {category}\naction label: {action}\n{summary}\n{'=' * 40}")

        if do_sum_eval:
            summary_evaluation_data.source_texts.append(mail.body)
            summary_evaluation_data.summarized_texts.append(summary)
            summary_evaluation_data.reference_texts.append(mail.subject)

    # Summary Evaluation
    if do_sum_eval:
        summary_results = evaluate_summary(
            config,
            summary_evaluation_data.source_texts,
            summary_evaluation_data.summarized_texts,
            summary_evaluation_data.reference_texts,
        )
        print_evaluation_results(
            summary_results, eval_type="summary", additional=config.get("g_eval_additional", False)
        )


def generate_report(mail_dict: dict[str, Mail], config: dict):
    embedding_manager = EmbeddingManager(
        embedding_model_name=config["embedding"]["model_name"],
        similarity_metric=config["embedding"]["similarity_metric"],
        similarity_threshold=config["embedding"]["similarity_threshold"],
        is_save_results=config["embedding"]["save_results"],
    )
    embedding_manager.run(mail_dict)


def add_reflexion(mail_dict: dict[str, Mail], api_key: str, config: dict):
    summary_agent = SummaryAgent(
        model_name="solar-pro",
        summary_type="final",
        api_key=api_key,
        temperature=config["temperature"]["summary"],
        seed=config["seed"],
    )

    origin_mail = ""
    for mail_id, mail in mail_dict.items():
        origin_mail += mail.summary + "\n"

    print(f"origin_mail:{origin_mail}\n")

    self_reflection_agent = ReflexionFramework("solar_pro", "final", config)

    reflexion_summary, token_usage = run_with_retry(self_reflection_agent.process, origin_mail, summary_agent)
    print(f"reflexion_summary:{reflexion_summary}")
    print(f"token_usage:{token_usage}")

    return reflexion_summary


def summary_and_report(gmail_service: GmailService, api_key: str):
    load_dotenv()

    # YAML 파일 로드
    config = load_config()

    try:
        mail_dict: dict[str, Mail] = fetch_mails(
            gmail_service=gmail_service,
            start_date=config["gmail"]["start_date"],
            end_date=config["gmail"]["end_date"],
            n=config["gmail"]["max_mails"],
        )

        summary_and_classify(mail_dict, config, api_key)

        generate_report(mail_dict, config)

        report = add_reflexion(mail_dict, api_key, config)

        df = convert_mail_dict_to_df(mail_dict)

        json_checklist = build_json_checklist(df)
        print(json_checklist)
        return json_checklist, report

    except HttpError as error:
        print(f"An error occurred: {error}")
    except openai.RateLimitError as rate_err:
        print("[RateLimitError] API 한도가 초과되었습니다. 현재까지의 토큰 사용량만 보고합니다.")
        print(f"에러 메세지: {rate_err}")
