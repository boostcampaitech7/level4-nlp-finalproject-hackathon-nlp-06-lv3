import os
import time

import openai
from dotenv import load_dotenv
from googleapiclient.errors import HttpError

from agents import BaseAgent, ClassificationAgent, ClassificationType, EmbeddingManager, SelfRefineAgent, SummaryAgent
from evaluation import ClassificationEvaluationAgent, print_evaluation_results, summary_evaluation_data
from evaluator import evaluate_summary
from gmail_api import Mail
from markdown_report import build_and_save_markdown_report
from utils import TokenManager, convert_mail_dict_to_df, fetch_mails, load_config, print_result, run_with_retry


def summary_and_classify(mail_dict: dict[str, Mail], config: dict, api_key):
    # 개별 메일 요약, 분류
    summary_agent = SummaryAgent("solar-pro", "single", api_key, config["temperature"]["summary"], config["seed"])
    self_refine_agent = SelfRefineAgent(
        "solar-pro", "single", api_key, config["temperature"]["summary"], config["seed"]
    )  # TODO: reflexion으로 변경 실험
    classification_agent = ClassificationAgent(
        "solar-pro", api_key, config["temperature"]["classification"], config["seed"]
    )
    if config["evaluation"]["classification_eval"]:
        class_eval_agent = ClassificationEvaluationAgent(
            model="gpt-4o",
            human_evaluation=config["classification"]["do_manual_filter"],
            inference=config["classification"]["inference"],
        )

    for mail_id, mail in mail_dict.items():
        summary, token_usage = run_with_retry(self_refine_agent.process, mail, summary_agent)
        mail_dict[mail_id].summary = summary
        TokenManager.total_token_usage += token_usage

        if config["evaluation"]["classification_eval"]:
            category = run_with_retry(class_eval_agent.process, mail, classification_agent, ClassificationType.CATEGORY)
            action = run_with_retry(class_eval_agent.process, mail, classification_agent, ClassificationType.ACTION)
        else:
            category = run_with_retry(classification_agent.process, mail, ClassificationType.CATEGORY)
            action = run_with_retry(classification_agent.process, mail, ClassificationType.ACTION)
        mail_dict[mail_id].label_category = category
        mail_dict[mail_id].label_action = action

        print(f"{mail_id}\ncategory label: {category}\naction label: {action}\n{summary}\n{'=' * 40}")

        if config["evaluation"]["summary_eval"]:
            summary_evaluation_data.source_texts.append(mail.body)
            summary_evaluation_data.summarized_texts.append(summary)
            summary_evaluation_data.reference_texts.append(mail.subject)

    # Summary Evaluation
    if config["evaluation"]["summary_eval"]:
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


def main():
    load_dotenv()
    api_key = os.getenv("UPSTAGE_API_KEY")
    # YAML 파일 로드
    config = load_config()

    try:
        mail_dict: dict[str, Mail] = fetch_mails(
            start_date=config["gmail"]["start_date"],
            end_date=config["gmail"]["end_date"],
            n=config["gmail"]["max_mails"],
        )

        start_time = time.time()

        summary_and_classify(mail_dict, config, api_key)

        generate_report(mail_dict, config)

        print_result(start_time, mail_dict)

        df = convert_mail_dict_to_df(mail_dict)

        markdown_report = build_and_save_markdown_report(df)

        return markdown_report

    except HttpError as error:
        print(f"An error occurred: {error}")
    except openai.RateLimitError as rate_err:
        print("[RateLimitError] API 한도가 초과되었습니다. 현재까지의 토큰 사용량만 보고합니다.")
        print(f"에러 메세지: {rate_err}")
    finally:
        if config["token_tracking"]:
            BaseAgent.plot_token_cost()


if __name__ == "__main__":
    main()
