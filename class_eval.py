import warnings

from dotenv import load_dotenv
from tqdm import tqdm

from agents import ClassificationAgent
from evaluation import ClassificationEvaluationAgent, fetch_emails, load_mail_dict, parse_arguments, save_mail_dict
from gmail_api import GmailService


def load_or_fetch_emails(mail_dict_path, gmail_service, date, n):
    """메일 데이터를 로드하거나 없을 경우 새로 가져옵니다."""
    mail_dict = load_mail_dict(mail_dict_path)
    if mail_dict is None:
        mail_dict = fetch_emails(gmail_service, date, n)
        save_mail_dict(mail_dict, mail_dict_path)
    return mail_dict


def evaluate_emails(
    mail_dict: dict, classification_agent: ClassificationAgent, evaluation_agent: ClassificationEvaluationAgent
):
    """메일 데이터를 평가하는 함수."""
    for mail_id, mail in tqdm(mail_dict.items(), desc="이메일 평가 진행 중"):
        mail_dict[mail_id] = evaluation_agent.process(mail, classification_agent)


def main():
    """메일 데이터를 가져와 AI 모델을 사용하여 분류하고 평가하는 메인 실행 함수."""
    load_dotenv()
    warnings.filterwarnings(action="ignore")

    args = parse_arguments()

    gmail_service = GmailService()
    N = 10
    mail_dict_path = f"evaluation/classification/mails_{N}.pkl"
    mail_dict = load_or_fetch_emails(mail_dict_path, gmail_service, "2025/01/10", N)

    classification_agent = ClassificationAgent(model_name="solar-pro")
    evaluation_agent = ClassificationEvaluationAgent(
        model="gpt-4o", human_evaluation=args.human_evaluation, inference=5  # args.inference
    )

    evaluate_emails(mail_dict, classification_agent, evaluation_agent)

    evaluation_agent.print_evaluation()


if __name__ == "__main__":
    main()
