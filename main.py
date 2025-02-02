from dotenv import load_dotenv
from googleapiclient.errors import HttpError

from agents import ClassificationAgent, SelfRefineAgent, SummaryAgent
from evaluation import format_source_texts_for_report, generate_final_report_text, print_evaluation_results
from evaluator import evaluate_report, evaluate_summary
from gmail_api import Mail
from utils import fetch_mails, load_config, print_result, run_with_retry

# from reflexion import
#     ReflexionActorSummaryAgent,
#     ReflexionEvaluator,
#     ReflexionFramework,
#     ReflexionSelfReflection


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

        # 개별 메일 요약, 분류
        summay_agent = SummaryAgent("solar-pro", "single")
        classification_agent = ClassificationAgent("solar-pro")

        # 평가용 데이터 저장
        source_texts = []
        summarized_texts = []
        reference_texts = []

        for mail_id, mail in mail_dict.items():
            summary = run_with_retry(summay_agent.process, mail)
            category = run_with_retry(classification_agent.process, mail)
            mail_dict[mail_id].summary = summary["summary"]
            mail_dict[mail_id].label = category

            print(mail_id)
            print(category)
            print(summary)
            print("=" * 40)

            source_texts.append(mail.body)
            summarized_texts.append(summary["summary"])
            reference_texts.append(mail.subject)

        # Summary Evaluation
        if config["evaluation"]["summary_eval"]:
            summary_results = evaluate_summary(config, source_texts, summarized_texts, reference_texts)
            print_evaluation_results(
                summary_results, eval_type="summary", additional=config.get("g_eval_additional", False)
            )

        # 주석 책갈피1 시작
        report_agent = SummaryAgent("solar-pro", "final")
        self_refine_agent = SelfRefineAgent("solar-pro", "final")

        report: dict = run_with_retry(self_refine_agent.process, mail_dict, report_agent, 10)

        print_result(config["gmail"]["start_date"], report, mail_dict)

        # 주석 책갈피1 끝

        # 주석 책갈피1 부분 주석 처리 하고 주석 책갈피 2 해제 (맨위 reflexion import 부분도 주석 해제할것)
        # 주석 책갈피2 시작
        # report_agent = SummaryAgent("solar-pro", "final")
        # report = report_agent.process(mail_dict)

        # task = "final_report"

        # # SummaryAgent에서 나온 출력물을 Evaluator, SelfReflection에 전달해주기 위해 전처리하는 과정

        # if task == "final_report":
        #     initial_output_text = ""
        #     for label, mail_reports in report.items():
        #         initial_output_text += f"{map_category(label)}\n"
        #         count = 1
        #         for mail_report in mail_reports:
        #             initial_output_text += f"{count}. {mail_report['report']}\n"
        #             count += 1
        #         initial_output_text += "\n\n"
        # elif task == "single":
        #     initial_output_text = report.get("summary")

        # report_agent = SummaryAgent("solar-pro", "final")
        # task = "final_report"
        # summary_type = task.split("_")[0]
        # actor = ReflexionActorSummaryAgent(model_name="solar-pro", summary_type=summary_type)
        # evaluator = ReflexionEvaluator(task)
        # self_reflection = ReflexionSelfReflection(task)

        # reflexion = ReflexionFramework(task=task, actor=actor, evaluator=evaluator, self_reflection=self_reflection)
        # reflexion.run(
        #     source_text=mail_dict,
        #     initial_output_text=initial_output_text,
        #     max_iteration=10,
        #     threshold="average",
        #     score_threshold=4.5,
        # )
        # 주석 책갈피2 끝

        # Report Evaluation
        if config["evaluation"]["report_eval"]:
            report_texts = []
            report_texts.append(generate_final_report_text(report, mail_dict))
            summarized = []
            summarized.append(format_source_texts_for_report(summarized_texts))
            references = []
            references.append("gold")

            report_results = evaluate_report(config, summarized, report_texts, references)
            print_evaluation_results(report_results, eval_type="report", additional=True)

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
