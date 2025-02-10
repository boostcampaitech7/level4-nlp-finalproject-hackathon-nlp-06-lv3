import warnings
from collections import Counter

import pandas as pd

from agents.classification.classification_agent import ClassificationAgent
from agents.classification.classification_type import ClassificationType
from gmail_api.mail import Mail
from utils.configuration import Config

warnings.filterwarnings("ignore", message="A single label was found in 'y_true' and 'y_pred'.*")


def classify_single_mail(mail_dict: dict[str, Mail], summary_dict: dict[str, str]) -> tuple[dict, dict]:
    temperature: int = Config.config["temperature"]["classification"]
    seed: int = Config.config["seed"]

    classification_agent = ClassificationAgent("solar-pro", temperature, seed)

    categories_dict = {}
    actions_dict = {}

    iteration = Config.config["classification"]["inference"]

    df = pd.DataFrame(columns=["categories", "actions"], index=list(mail_dict.keys()))
    df.index.name = "id"

    for mail_id, mail in mail_dict.items():
        categories = [
            classification_agent.process(summary_dict[mail_id], ClassificationType.CATEGORY) for i in range(iteration)
        ]
        actions = [
            classification_agent.process(summary_dict[mail_id], ClassificationType.ACTION) for i in range(iteration)
        ]

        categories_dict[mail_id] = categories
        actions_dict[mail_id] = actions

        df.loc[mail_id, ["categories", "actions"]] = [categories, actions]

    df.to_csv("evaluation/data/generated_category.csv")

    category_dict = {
        mail_id: Counter(categories).most_common(1)[0][0] for mail_id, categories in categories_dict.items()
    }
    action_dict = {mail_id: Counter(actions).most_common(1)[0][0] for mail_id, actions in actions_dict.items()}

    return category_dict, action_dict
