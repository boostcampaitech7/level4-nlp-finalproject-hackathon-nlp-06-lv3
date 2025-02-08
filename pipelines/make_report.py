from agents.reflexion.reflexion import ReflexionFramework
from agents.summary.summary_agent import SummaryAgent
from utils.configuration import Config


def make_report(summary_dict: dict[str, str]):
    summary_agent = SummaryAgent(
        model_name="solar-pro",
        summary_type="final",
        temperature=Config.config["temperature"]["summary"],
        seed=Config.config["seed"],
    )

    origin_mail = "\n".join(summary_dict.values())

    self_reflection_agent = ReflexionFramework("final")

    reflexion_summary = self_reflection_agent.process(origin_mail, summary_agent)

    return reflexion_summary
