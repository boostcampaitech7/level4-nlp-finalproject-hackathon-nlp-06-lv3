from agents.self_refine.self_refine_agent import SelfRefineAgent
from agents.summary.summary_agent import SummaryAgent
from evaluation.evaluation_data import summary_evaluation_data
from evaluation.evaluation_summary import evaluate_summary
from evaluation.result_printer import print_evaluation_results
from gmail_api.mail import Mail
from utils.configuration import Config


def summary_single_mail(mail_dict: dict[str, Mail], api_key: str):
    temperature: int = Config.config["temperature"]["summary"]
    seed: int = Config.config["seed"]
    do_sum_eval: bool = Config.config["evaluation"]["summary_eval"]

    summary_agent = SummaryAgent("solar-pro", "single", api_key, temperature, seed)
    self_refine_agent = SelfRefineAgent("solar-pro", "single", api_key, temperature, seed)
    for mail_id, mail in mail_dict.items():
        summary = self_refine_agent.process(mail, summary_agent)
        mail_dict[mail_id].summary = summary

        if do_sum_eval:
            summary_evaluation_data.source_texts.append(mail.body)
            summary_evaluation_data.summarized_texts.append(summary)
            summary_evaluation_data.reference_texts.append(mail.subject)

    if do_sum_eval:
        summary_results = evaluate_summary(
            summary_evaluation_data.source_texts,
            summary_evaluation_data.summarized_texts,
            summary_evaluation_data.reference_texts,
        )
        print_evaluation_results(summary_results, eval_type="summary")
