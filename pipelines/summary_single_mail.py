from agents.self_refine.self_refine_agent import SelfRefineAgent
from agents.summary.summary_agent import SummaryAgent
from gmail_api.mail import Mail
from utils.configuration import Config


def summary_single_mail(mail_dict: dict[str, Mail]) -> dict[str, str]:
    temperature: int = Config.config["temperature"]["summary"]
    seed: int = Config.config["seed"]

    summary_dict = {}
    summary_agent = SummaryAgent("solar-pro", "single", temperature, seed)
    self_refine_agent = SelfRefineAgent("solar-pro", temperature, seed)
    for mail_id, mail in mail_dict.items():
        summary = summary_agent.process(str(mail))
        refined_summary = self_refine_agent.process(mail, summary)
        summary_dict[mail_id] = refined_summary

    return summary_dict
