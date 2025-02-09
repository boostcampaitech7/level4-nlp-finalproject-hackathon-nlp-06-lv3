from evaluation.gpt_eval import calculate_g_eval
from evaluation.quantitative_eval import calculate_bert, calculate_rouge
from utils.configuration import Config


def evaluate_summary(source_texts, report_texts, reference_texts):
    """
    설정(config)에 따라 ROUGE / BERT / G-EVAL 계산
    """
    summary_config = Config.config["summary"]  # summary 설정 가져오기
    metrics = summary_config["metrics"]  # summary의 평가 메트릭 리스트
    results = {}

    # ROUGE 평가
    if "rouge" in metrics:
        results["rouge"] = calculate_rouge(reference_texts, report_texts)

    # BERT 평가
    if "bert" in metrics:
        bert_model = summary_config.get("bert_model", "distilbert-base-uncased")
        results["bert"] = calculate_bert(reference_texts, report_texts, model_type=bert_model)

    # G-EVAL 평가 (기본 4개 / 추가 옵션 포함 가능)
    if "g-eval" in metrics:
        model_name = Config.config["summary"]["g_eval"]["openai_model"]
        results["g-eval"] = calculate_g_eval(
            source_texts=source_texts,
            generated_texts=report_texts,
            eval_type="summary",
            model_name=model_name,
        )

    return results
