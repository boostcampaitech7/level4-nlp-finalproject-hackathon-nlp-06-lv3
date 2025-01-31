from evaluation import calculate_rouge
from evaluation import calculate_bert
from evaluation import calculate_g_eval


def evaluate_summary(config, source_texts, report_texts, reference_texts):
    """
    설정(config)에 따라 ROUGE / BERT / G-EVAL 계산
    """
    metrics = config.get("metrics", [])
    results = {}

    # ROUGE 평가
    if "rouge" in metrics:
        results["rouge"] = calculate_rouge(reference_texts, report_texts)

    # BERT 평가
    if "bert" in metrics:
        results["bert"] = calculate_bert(
            reference_texts, report_texts, model_type=config.get("bert_model", "distilbert-base-uncased")
        )

    # G-EVAL 평가 (기본 4개 / 추가 옵션 포함 가능)
    if "g-eval" in metrics:
        g_eval_additional = config.get("g_eval_additional", False)  # 기본값 False
        results["g-eval"] = calculate_g_eval(
            source_texts, report_texts, config, eval_type="summary", additional=g_eval_additional
        )

    return results


def evaluate_report(config, source_texts, report_texts, reference_texts):
    """
    설정(config)에 따라 Final Report에 대해 G-EVAL 평가 수행.
    - 기본적으로 G-EVAL만 사용 (ROUGE / BERT 없음)
    - additional=True로 항상 7개 평가 기준 적용
    """
    metrics = config.get("metrics", [])
    results = {}

    # G-EVAL 평가 (항상 additional=True)
    if "g-eval" in metrics:
        results["g-eval"] = calculate_g_eval(source_texts, report_texts, config, eval_type="report", additional=True)

    return results
