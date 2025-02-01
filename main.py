from datetime import datetime  # , timedelta

from dotenv import load_dotenv
from googleapiclient.errors import HttpError
from tqdm import tqdm

from agents import ClassificationAgent, SelfRefineAgent, SummaryAgent, map_category
from gmail_api import GmailService, Mail

# from reflexion import
#     ReflexionActorSummaryAgent,
#     ReflexionEvaluator,
#     ReflexionFramework,
#     ReflexionSelfReflection

from evaluation import load_config


def main():
    load_dotenv()

    config = load_config("config.yml")

    try:
        gmail_service = GmailService()

        # Fetch last N messages
        today = datetime.now().strftime("%Y/%m/%d")
        yesterday = "2025/01/10"  # (datetime.today() - timedelta(days=1)).strftime("%Y/%m/%d")
        n = 10

        messages = gmail_service.get_today_n_messages(yesterday, n)
        mail_dict: dict[str, Mail] = {}
        for idx, message_metadata in enumerate(tqdm(messages, desc="Processing Emails")):
            # 신규 mail_id 정의: 받은 시간 순 오름차순
            mail_id = f"{today}/{len(messages)-idx:04d}"
            mail = Mail(message_metadata["id"], mail_id, gmail_service)
            # 룰베이스 분류
            if "(광고)" not in mail.subject:
                mail_dict[mail_id] = mail

        # 개별 메일 요약, 분류
        summay_agent = SummaryAgent("solar-pro", "single")
        classification_agent = ClassificationAgent("solar-pro")

        # 평가용 데이터 저장
        source_texts = []
        summarized_texts = []

        for mail_id, mail in mail_dict.items():
            summary = summay_agent.process(mail)
            category = classification_agent.process(mail)
            mail_dict[mail_id].summary = summary["summary"]
            mail_dict[mail_id].label = category

            print(mail_id)
            print(category)
            print(summary)
            print("=" * 40)

            source_texts.append(mail.body)
            summarized_texts.append(summary["summary"])

        # Summary Evaluation
        if config.summary_eval:
            # TODO: 요약에 대한 G-EVAL 점수 출력
            pass

        # 주석 책갈피1 시작
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
        if config.report_eval:
            # TODO: 레포트에 대한 G-EVAL 점수 출력
            pass

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
