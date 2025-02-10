import warnings

from agents.classification.classification_agent import ClassificationAgent
from agents.classification.classification_type import ClassificationType
from gmail_api.mail import Mail
from utils.configuration import Config

warnings.filterwarnings("ignore", message="A single label was found in 'y_true' and 'y_pred'.*")


def classify_single_mail(mail_dict: dict[str, Mail], summary_dict: dict[str, str]) -> tuple[dict, dict]:
    temperature: int = Config.config["temperature"]["classification"]
    seed: int = Config.config["seed"]

    classification_agent = ClassificationAgent("solar-pro", temperature, seed)

    category_dict = {}
    action_dict = {}

    for mail_id, mail in mail_dict.items():
        category = classification_agent.process(summary_dict[mail_id], ClassificationType.CATEGORY)
        action = classification_agent.process(summary_dict[mail_id], ClassificationType.ACTION)

        category_dict[mail_id] = category
        action_dict[mail_id] = action

    return category_dict, action_dict
