from agents.reflexion.reflexion import ReflexionFramework
from agents.summary.summary_agent import SummaryAgent
from gmail_api.mail import Mail
from utils.configuration import Config


def make_report(mail_dict: dict[str, Mail], api_key: str):
    summary_agent = SummaryAgent(
        model_name="solar-pro",
        summary_type="final",
        api_key=api_key,
        temperature=Config.config["temperature"]["summary"],
        seed=Config.config["seed"],
    )

    origin_mail = ""
    for _, mail in mail_dict.items():
        origin_mail += mail.summary + "\n"

    self_reflection_agent = ReflexionFramework("final")

    reflexion_summary = self_reflection_agent.process(origin_mail, summary_agent)

    return reflexion_summary
