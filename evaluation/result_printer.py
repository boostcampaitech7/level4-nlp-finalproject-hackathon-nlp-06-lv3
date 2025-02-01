def print_individual_scores(results, eval_type, additional):
    """
    개별 샘플의 점수를 출력하는 함수
    """
    n_items = len(next(iter(results.values())))  # 결과 리스트 길이 가져오기

    for i in range(n_items):
        print(f"\n--- {eval_type.capitalize()} Sample {i+1} ---")

        # ROUGE 출력 (Summary만)
        if eval_type == "summary" and "rouge" in results:
            ritem = results["rouge"][i]
            print(
                f"[ROUGE] R1=(P:{ritem['rouge1'][0]:.4f},R:{ritem['rouge1'][1]:.4f},F:{ritem['rouge1'][2]:.4f}), "
                f"R2=(P:{ritem['rouge2'][0]:.4f},R:{ritem['rouge2'][1]:.4f},F:{ritem['rouge2'][2]:.4f}), "
                f"RL=(P:{ritem['rougeL'][0]:.4f},R:{ritem['rougeL'][1]:.4f},F:{ritem['rougeL'][2]:.4f})"
            )

        # BERT 출력 (Summary만)
        if eval_type == "summary" and "bert" in results:
            bp, br, bf = results["bert"][i]
            print(f"[BERT] P:{bp:.4f}, R:{br:.4f}, F:{bf:.4f}")

        # G-EVAL 출력 (Summary & Report 공통)
        if "g-eval" in results:
            gitem = results["g-eval"][i]
            print(
                "[G-EVAL] "
                f"consistency={gitem['consistency']:.4f}, "
                f"coherence={gitem['coherence']:.4f}, "
                f"fluency={gitem['fluency']:.4f}, "
                f"relevance={gitem['relevance']:.4f}"
            )

            # 추가 G-EVAL 항목 출력 (additional=True일 때)
            if additional:
                print(
                    "[G-EVAL Additional] "
                    f"readability={gitem['readability']:.4f}, "
                    f"clearance={gitem['clearance']:.4f}, "
                    f"practicality={gitem['practicality']:.4f}"
                )


def calculate_average_scores(results, eval_type: str, n_items: int, additional: bool) -> dict:
    """
    결과 데이터에서 평균 점수를 계산하는 함수.

    Args:
        results (dict): 평가 결과 데이터.
        eval_type (str): 평가 유형 ("summary" 또는 "report").
        n_items (int): 총 평가 개수.
        additional (bool): 추가 평가 항목 포함 여부.

    Returns:
        dict: 평균 점수를 담은 딕셔너리.
    """
    avg_scores = {}

    # ROUGE 평균 (Summary만)
    if eval_type == "summary" and "rouge" in results:
        rouge_list = results["rouge"]
        rouge_keys = ["r1_p", "r1_r", "r1_f", "r2_p", "r2_r", "r2_f", "rl_p", "rl_r", "rl_f"]
        avg_scores["rouge"] = {k: 0.0 for k in rouge_keys}

        for item in rouge_list:
            for key, (p, r, f) in zip(rouge_keys, item.values()):
                avg_scores["rouge"][key] += p if "p" in key else r if "r" in key else f

        avg_scores["rouge"] = {k: v / n_items for k, v in avg_scores["rouge"].items()}

    # BERT 평균 (Summary만)
    if eval_type == "summary" and "bert" in results:
        p_sum, r_sum, f_sum = 0.0, 0.0, 0.0
        for p, r, f in results["bert"]:
            p_sum += p
            r_sum += r
            f_sum += f
        avg_scores["bert"] = {
            "precision": p_sum / n_items,
            "recall": r_sum / n_items,
            "f1": f_sum / n_items,
        }

    # G-EVAL 평균 (Summary & Report 공통)
    if "g-eval" in results:
        geval_list = results["g-eval"]
        eval_keys = ["consistency", "coherence", "fluency", "relevance"]
        if additional:
            eval_keys.extend(["readability", "clearance", "practicality"])

        avg_scores["g-eval"] = {k: 0.0 for k in eval_keys}

        for item in geval_list:
            for key in eval_keys:
                avg_scores["g-eval"][key] += item.get(key, 0.0)

        avg_scores["g-eval"] = {k: v / n_items for k, v in avg_scores["g-eval"].items()}

    return avg_scores


def print_average_scores(results: dict, eval_type: str, n_items: int, additional: bool) -> None:
    """
    평가 결과의 평균 점수를 출력하는 함수.

    Args:
        results (dict): 평가 결과 데이터.
        eval_type (str): 평가 유형 ("summary" 또는 "report").
        n_items (int): 총 평가 개수.
        additional (bool): 추가 평가 항목 포함 여부.
    """
    print("\n===== Averages =====")

    avg_scores = calculate_average_scores(results, eval_type, n_items, additional)

    # ROUGE 평균 출력 (Summary만)
    if eval_type == "summary" and "rouge" in avg_scores:
        print("\n[ROUGE Avg]")
        print(
            f"  ROUGE-1: P={avg_scores['rouge']['r1_p']:.4f}, "
            f"R={avg_scores['rouge']['r1_r']:.4f}, "
            f"F1={avg_scores['rouge']['r1_f']:.4f}"
        )
        print(
            f"  ROUGE-2: P={avg_scores['rouge']['r2_p']:.4f}, "
            f"R={avg_scores['rouge']['r2_r']:.4f}, "
            f"F1={avg_scores['rouge']['r2_f']:.4f}"
        )
        print(
            f"  ROUGE-L: P={avg_scores['rouge']['rl_p']:.4f}, "
            f"R={avg_scores['rouge']['rl_r']:.4f}, "
            f"F1={avg_scores['rouge']['rl_f']:.4f}"
        )

    # BERT 평균 출력 (Summary만)
    if eval_type == "summary" and "bert" in avg_scores:
        print("\n[BERT Avg]")
        print(
            f"  Precision: {avg_scores['bert']['precision']:.4f}, "
            f"Recall: {avg_scores['bert']['recall']:.4f}, "
            f"F1: {avg_scores['bert']['f1']:.4f}"
        )

    # G-EVAL 평균 출력 (Summary & Report 공통)
    if "g-eval" in avg_scores:
        print("\n[G-EVAL Avg]")
        print(
            f"  consistency={avg_scores['g-eval']['consistency']:.4f}, "
            f"coherence={avg_scores['g-eval']['coherence']:.4f}, "
            f"fluency={avg_scores['g-eval']['fluency']:.4f}, "
            f"relevance={avg_scores['g-eval']['relevance']:.4f}"
        )

        if additional:
            print(
                f"  readability={avg_scores['g-eval']['readability']:.4f}, "
                f"clearance={avg_scores['g-eval']['clearance']:.4f}, "
                f"practicality={avg_scores['g-eval']['practicality']:.4f}"
            )


def print_evaluation_results(results, eval_type, additional=False):
    """
    Summary 또는 Report 평가 결과를 보기 좋게 출력하는 메인 함수
    """
    print(f"\n===== {eval_type.upper()} Evaluation Results =====")

    # 개별 샘플 점수 출력
    print_individual_scores(results, eval_type, additional)

    # 평균 점수 출력
    n_items = len(next(iter(results.values())))  # 결과 리스트 길이 가져오기
    print_average_scores(results, eval_type, n_items, additional)
