import pandas as pd

from agents.reflexion.reflexion import ReflexionFramework


def make_report(summary_dict: dict[str, str]):

    origin_mail = "\n".join(summary_dict.values())
    self_reflection_agent = ReflexionFramework()
    reflexion_summary = self_reflection_agent.process(origin_mail)

    pd.DataFrame({"source": [origin_mail], "report": [reflexion_summary]}).to_csv(
        "evaluation/data/generated_report.csv", index=False
    )

    return reflexion_summary
