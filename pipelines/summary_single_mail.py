import pandas as pd

from agents.self_refine.self_refine_agent import SelfRefineAgent
from agents.summary.summary_agent import SummaryAgent
from gmail_api.mail import Mail
from utils.configuration import Config


def summary_single_mail(mail_dict: dict[str, Mail]) -> dict[str, str]:
    temperature: int = Config.config["temperature"]["summary"]
    seed: int = Config.config["seed"]

    summary_agent = SummaryAgent("solar-pro", "single", temperature, seed)
    self_refine_agent = SelfRefineAgent("solar-pro", temperature, seed)

    summary_dict = {
        mail_id: self_refine_agent.process(mail, summary_agent.process(str(mail)))
        for mail_id, mail in mail_dict.items()
    }

    pd.DataFrame.from_dict(summary_dict, orient="index", columns=["summary"]).to_csv(
        "evaluation/data/generated_summary.csv", index_label="id"
    )

    return summary_dict
