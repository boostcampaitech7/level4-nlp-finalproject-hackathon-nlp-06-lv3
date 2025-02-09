import warnings

from agents.classification.classification_agent import ClassificationAgent
from agents.classification.classification_type import ClassificationType
from evaluation.classification.evaluation_agent import ClassificationEvaluationAgent
from gmail_api.mail import Mail
from utils.configuration import Config

warnings.filterwarnings("ignore", message="A single label was found in 'y_true' and 'y_pred'.*")


def classify_single_mail(mail_dict: dict[str, Mail], summary_dict: dict[str, str]) -> tuple[dict, dict]:
    temperature: int = Config.config["temperature"]["classification"]
    seed: int = Config.config["seed"]
    do_class_eval: bool = Config.config["evaluation"]["classification_eval"]

    classification_agent = ClassificationAgent("solar-pro", temperature, seed)
    if do_class_eval:
        category_class_eval_agent = ClassificationEvaluationAgent(
            model_name="solar-pro",
            human_evaluation=Config.config["classification"]["do_manual_filter"],
            inference_iteration=Config.config["classification"]["inference"],
            classification_type=ClassificationType.CATEGORY,
        )
        action_class_eval_agent = ClassificationEvaluationAgent(
            model_name="solar-pro",
            human_evaluation=Config.config["classification"]["do_manual_filter"],
            inference_iteration=Config.config["classification"]["inference"],
            classification_type=ClassificationType.ACTION,
        )

    category_dict = {}
    action_dict = {}

    for mail_id, mail in mail_dict.items():
        if do_class_eval:
            category = category_class_eval_agent.process(mail, summary_dict[mail_id], classification_agent)
            action = action_class_eval_agent.process(mail, summary_dict[mail_id], classification_agent)
        else:
            category = classification_agent.process(summary_dict[mail_id], ClassificationType.CATEGORY)
            action = classification_agent.process(summary_dict[mail_id], ClassificationType.ACTION)

        category_dict[mail_id] = category
        action_dict[mail_id] = action

    if do_class_eval:
        category_class_eval_agent.print_evaluation()
        action_class_eval_agent.print_evaluation()

    return category_dict, action_dict
