import openai
from dotenv import load_dotenv
from googleapiclient.errors import HttpError

from agents import BaseAgent, ClassificationAgent, EmbeddingManager, SelfRefineAgent, SummaryAgent
from evaluation import ClassificationEvaluationAgent, print_evaluation_results, summary_evaluation_data
from evaluator import evaluate_summary
from gmail_api import Mail
from utils import TokenManager, fetch_mails, load_config, run_with_retry


def summary_and_classify(mail_dict: dict[str, Mail], config: dict):
    # 개별 메일 요약, 분류
    summary_agent = SummaryAgent("solar-pro", "single")
    self_refine_agent = SelfRefineAgent("solar-pro", "single")  # TODO: reflexion으로 변경 실험
    classification_agent = ClassificationAgent("solar-pro")
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
            category = run_with_retry(class_eval_agent.process, mail, classification_agent)
        else:
            category = run_with_retry(classification_agent.process, mail)
        mail_dict[mail_id].label_category = category

        print(f"{mail_id}\n{category}\n{summary}\n{'=' * 40}")

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
    # TODO: 리포트 생성 로직 변경하기
    embedding_manager = EmbeddingManager("upstage", "dot-product", is_save_results=True)
    clustred_mails = embedding_manager.run(mail_dict)

    for category, similar_mail_dict in clustred_mails.items():
        print(f"{'=' * 40}\n분류: {category}")
        for mail_id, similar_mail_list in similar_mail_dict.items():
            sim_summary = "\n".join(
                [f"{i}위 요약문: {mail_dict[sim_mail_id].summary}" for i, sim_mail_id in enumerate(similar_mail_list)]
            )
            print(f"메일 ID: {mail_id}\n요약문: {mail_dict[mail_id].summary}\n{sim_summary}")
        print()


def main():
    load_dotenv()

    # YAML 파일 로드
    config = load_config()

    try:
        mail_dict: dict[str, Mail] = fetch_mails(
            start_date=config["gmail"]["start_date"],
            end_date=config["gmail"]["end_date"],
            n=config["gmail"]["max_mails"],
        )

        # start_time = time.time()

        summary_and_classify(mail_dict, config)

        generate_report(mail_dict, config)

        # print_result(start_time, report, mail_dict)

    except HttpError as error:
        print(f"An error occurred: {error}")
    except openai.RateLimitError as rate_err:
        print("[RateLimitError] API 한도가 초과되었습니다. 현재까지의 토큰 사용량만 보고합니다.")
        print(f"에러 메세지: {rate_err}")
    finally:
        BaseAgent.plot_token_cost()


if __name__ == "__main__":
    main()
