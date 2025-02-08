from agents import ReflexionFramework, SummaryAgent
from gmail_api.mail import Mail


def make_report(mail_dict: dict[str, Mail], api_key: str, config: dict):
    summary_agent = SummaryAgent(
        model_name="solar-pro",
        summary_type="final",
        api_key=api_key,
        temperature=config["temperature"]["summary"],
        seed=config["seed"],
    )

    origin_mail = ""
    for _, mail in mail_dict.items():
        origin_mail += mail.summary + "\n"

    self_reflection_agent = ReflexionFramework("solar_pro", "final", config)

    reflexion_summary = self_reflection_agent.process(origin_mail, summary_agent)

    return reflexion_summary
