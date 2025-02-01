from evaluation import calculate_bert, calculate_g_eval, calculate_rouge


def evaluate_summary(config, source_texts, report_texts, reference_texts):
    """
    설정(config)에 따라 ROUGE / BERT / G-EVAL 계산
    """
    summary_config = config.get("summary", {})  # summary 설정 가져오기
    metrics = summary_config.get("metrics", [])  # summary의 평가 메트릭 리스트
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
        g_eval_config = summary_config.get("g_eval", {})  # g-eval 설정만 추출
        g_eval_additional = g_eval_config.get("additional", False)  # 추가 평가 여부
        results["g-eval"] = calculate_g_eval(
            source_texts, report_texts, g_eval_config, eval_type="summary", additional=g_eval_additional
        )

    return results


def evaluate_report(config, source_texts, report_texts, reference_texts):
    """
    설정(config)에 따라 Final Report에 대해 G-EVAL 평가 수행.
    - 기본적으로 G-EVAL만 사용 (ROUGE / BERT 없음)
    - additional=True로 항상 7개 평가 기준 적용
    """
    report_config = config.get("report", {})  # report 설정 가져오기
    metrics = report_config.get("metrics", [])  # report의 평가 메트릭 리스트

    results = {}

    # G-EVAL 평가 (항상 additional=True)
    if "g-eval" in metrics:
        g_eval_config = report_config.get("g_eval", {})  # g-eval 설정만 추출
        results["g-eval"] = calculate_g_eval(
            source_texts, report_texts, g_eval_config, eval_type="report", additional=True
        )

    return results
