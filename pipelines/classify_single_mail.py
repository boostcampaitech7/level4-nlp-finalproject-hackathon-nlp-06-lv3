import warnings
from collections import Counter

import pandas as pd

from agents.classification.classification_agent import ClassificationAgent
from agents.classification.classification_type import ClassificationType
from utils.configuration import Config

warnings.filterwarnings("ignore", message="A single label was found in 'y_true' and 'y_pred'.*")


def classify_single_mail(summary_dict: dict[str, str]) -> tuple[dict, dict]:
    temperature: int = Config.config["temperature"]["classification"]
    seed: int = Config.config["seed"]

    classification_agent = ClassificationAgent("solar-pro", temperature, seed)

    categories_dict = {}
    actions_dict = {}

    iteration = Config.config["classification"]["inference"]

    categories_dict = {
        mail_id: [
            classification_agent.process(summary_dict[mail_id], ClassificationType.CATEGORY) for _ in range(iteration)
        ]
        for mail_id in summary_dict
    }
    actions_dict = {
        mail_id: [
            classification_agent.process(summary_dict[mail_id], ClassificationType.ACTION) for _ in range(iteration)
        ]
        for mail_id in summary_dict
    }

    pd.DataFrame(
        {
            "id": list(summary_dict.keys()),
            "categories": list(categories_dict.values()),
            "actions": list(actions_dict.values()),
        },
        index=categories_dict.keys(),
    ).to_csv("evaluation/data/generated_category.csv", index=False)

    category_dict = {
        mail_id: Counter(categories).most_common(1)[0][0] for mail_id, categories in categories_dict.items()
    }
    action_dict = {mail_id: Counter(actions).most_common(1)[0][0] for mail_id, actions in actions_dict.items()}

    return category_dict, action_dict
