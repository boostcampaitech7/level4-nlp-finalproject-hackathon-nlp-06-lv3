from agents.classification.classification_agent import ClassificationAgent
from agents.classification.classification_type import ClassificationType
from evaluation.classification.evaluation_agent import ClassificationEvaluationAgent
from gmail_api.mail import Mail
from utils.configuration import Config


def classify_single_mail(mail_dict: dict[str, Mail]):
    temperature: int = Config.config["temperature"]["summary"]
    seed: int = Config.config["seed"]
    do_class_eval: bool = Config.config["evaluation"]["classification_eval"]

    classification_agent = ClassificationAgent("solar-pro", temperature, seed)
    if do_class_eval:
        class_eval_agent = ClassificationEvaluationAgent(
            model="gpt-4o",
            human_evaluation=Config.config["classification"]["do_manual_filter"],
            inference=Config.config["classification"]["inference"],
        )

    for mail_id, mail in mail_dict.items():
        if do_class_eval:
            category = class_eval_agent.process(mail, classification_agent, ClassificationType.CATEGORY)
            action = class_eval_agent.process(mail, classification_agent, ClassificationType.ACTION)
        else:
            category = classification_agent.process(mail, ClassificationType.CATEGORY)
            action = classification_agent.process(mail, ClassificationType.ACTION)
        mail_dict[mail_id].label_category = category
        mail_dict[mail_id].label_action = action
