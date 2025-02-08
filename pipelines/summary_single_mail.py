from agents.self_refine.self_refine_agent import SelfRefineAgent
from agents.summary.summary_agent import SummaryAgent
from evaluation.evaluation_summary import evaluate_summary
from evaluation.result_printer import print_evaluation_results
from gmail_api.mail import Mail
from utils.configuration import Config


def summary_single_mail(mail_dict: dict[str, Mail]) -> dict[str, str]:
    temperature: int = Config.config["temperature"]["summary"]
    seed: int = Config.config["seed"]
    do_sum_eval: bool = Config.config["evaluation"]["summary_eval"]

    source_texts = []
    summarized_texts = []
    reference_texts = []

    summary_dict = {}
    summary_agent = SummaryAgent("solar-pro", "single", temperature, seed)
    self_refine_agent = SelfRefineAgent("solar-pro", temperature, seed)
    for mail_id, mail in mail_dict.items():
        summary = summary_agent.process(str(mail))
        refined_summary = self_refine_agent.process(mail, summary)
        summary_dict[mail_id] = refined_summary

        if do_sum_eval:
            source_texts.append(mail.body)
            summarized_texts.append(refined_summary)
            reference_texts.append(mail.subject)

    if do_sum_eval:
        summary_results = evaluate_summary(
            source_texts,
            summarized_texts,
            reference_texts,
        )
        print_evaluation_results(summary_results, eval_type="summary")
    return summary_dict
