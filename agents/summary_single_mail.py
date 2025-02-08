from agents import SelfRefineAgent, SummaryAgent
from batch_serving import Mail
from evaluation import print_evaluation_results, summary_evaluation_data
from evaluator import evaluate_summary


def summary_single_mail(mail_dict: dict[str, Mail], config: dict, api_key: str):
    temperature: int = config["temperature"]["summary"]
    seed: int = config["seed"]
    do_sum_eval: bool = config["evaluation"]["summary_eval"]

    summary_agent = SummaryAgent("solar-pro", "single", api_key, temperature, seed)
    self_refine_agent = SelfRefineAgent("solar-pro", "single", api_key, temperature, seed)
    for mail_id, mail in mail_dict.items():
        summary, token_usage = self_refine_agent.process(mail, summary_agent)  # TODO: token_usage 미사용
        mail_dict[mail_id].summary = summary

        if do_sum_eval:
            summary_evaluation_data.source_texts.append(mail.body)
            summary_evaluation_data.summarized_texts.append(summary)
            summary_evaluation_data.reference_texts.append(mail.subject)

    if do_sum_eval:
        summary_results = evaluate_summary(
            config,
            summary_evaluation_data.source_texts,
            summary_evaluation_data.summarized_texts,
            summary_evaluation_data.reference_texts,
        )
        print_evaluation_results(
            summary_results, eval_type="summary", additional=config.get("g_eval_additional", False)
        )
