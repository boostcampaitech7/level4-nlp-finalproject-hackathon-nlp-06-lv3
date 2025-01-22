import argparse
import csv
import random

import torch
import yaml
from bert_score import score as bert_score
from rouge_score import rouge_scorer


def load_config(config_path):
    """
    주어진 경로의 YAML 파일을 로드해 dict 형태로 반환
    """
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


def load_data(csv_file):
    """
    CSV 파일에서 source, summarized, gold 열을 읽어 리스트로 반환
    """
    source_texts = []
    summarized_texts = []
    gold_texts = []

    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            source_texts.append(row["source"])
            summarized_texts.append(row["summarized"])
            gold_texts.append(row["gold"])

    return source_texts, summarized_texts, gold_texts


def calculate_rouge(gold_texts, generated_texts):
    """
    gold_texts, generated_texts: 길이 N 리스트
    각 쌍에 대해 ROUGE-1, ROUGE-2, ROUGE-L 계산
    return 형태 : [{"rouge1":(p,r,f), "rouge2":(p,r,f), "rougeL":(p,r,f)}, ...]
    """
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    results = []
    for gold, gen in zip(gold_texts, generated_texts):
        scores = scorer.score(gold, gen)
        item = {
            "rouge1": (
                scores["rouge1"].precision,
                scores["rouge1"].recall,
                scores["rouge1"].fmeasure,
            ),
            "rouge2": (
                scores["rouge2"].precision,
                scores["rouge2"].recall,
                scores["rouge2"].fmeasure,
            ),
            "rougeL": (
                scores["rougeL"].precision,
                scores["rougeL"].recall,
                scores["rougeL"].fmeasure,
            ),
        }
        results.append(item)
    return results


def calculate_bert(gold_texts, generated_texts, model_type="distilbert-base-uncased"):
    """
    BERTScore를 한 번에 계산 → 각 샘플별 (p, r, f) 튜플 리스트로 반환
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    P, R, F1 = bert_score(cands=generated_texts, refs=gold_texts, model_type=model_type, device=device)
    results = []
    for i in range(len(gold_texts)):
        results.append((P[i].item(), R[i].item(), F1[i].item()))
    return results


def calculate_g_eval(source_texts, generated_texts):
    """
    G-EVAL(gold 없이 source, summarized) 평가
    TODO: G-EVAL 방식으로 평가하여 점수 출력하는 코드 구현
    지금은 임시로 랜덤 점수가 출력
    """
    scores = []
    for src, gen in zip(source_texts, generated_texts):
        scores.append(random.uniform(0, 1))
    return scores  # 길이 N


def validate_data_lengths(metrics, source_texts, summarized_texts, gold_texts):
    """
    메트릭 종류에 따라 데이터 길이(source, gold 등)를 간단히 체크
    """
    n_summaries = len(summarized_texts)

    if "rouge" in metrics or "bert" in metrics:
        if len(gold_texts) != n_summaries:
            raise ValueError("CSV 내 gold 열과 summarized 열의 줄 수가 다릅니다.")
    if "g-eval" in metrics:
        if len(source_texts) != n_summaries:
            raise ValueError("CSV 내 source 열과 summarized 열의 줄 수가 다릅니다.")


def compute_metrics(config, source_texts, summarized_texts, gold_texts):
    """
    설정(config)에 따라 ROUGE / BERT / G-EVAL 계산
    """
    metrics = config.get("metrics", [])
    bert_model_type = config.get("bert_model", "distilbert-base-uncased")
    results = {}

    if "rouge" in metrics:
        rouge_res = calculate_rouge(gold_texts, summarized_texts)
        results["rouge"] = rouge_res

    if "bert" in metrics:
        bert_res = calculate_bert(gold_texts, summarized_texts, model_type=bert_model_type)
        results["bert"] = bert_res

    if "g-eval" in metrics:
        geval_res = calculate_g_eval(source_texts, summarized_texts)
        results["g-eval"] = geval_res

    return results


def print_per_item_scores(results, source_texts, summarized_texts, gold_texts):
    """
    각 샘플별(아이템별) 스코어를 출력
    """
    n_items = len(summarized_texts)
    for i in range(n_items):
        print(f"\n--- Sample {i+1} ---")

        # ROUGE
        if "rouge" in results:
            ritem = results["rouge"][i]
            r1p, r1r, r1f = ritem["rouge1"]
            r2p, r2r, r2f = ritem["rouge2"]
            rlp, rlr, rlf = ritem["rougeL"]
            print(
                f"[ROUGE] R1=(P:{r1p:.4f},R:{r1r:.4f},F:{r1f:.4f}), "
                f"R2=(P:{r2p:.4f},R:{r2r:.4f},F:{r2f:.4f}), "
                f"RL=(P:{rlp:.4f},R:{rlr:.4f},F:{rlf:.4f})"
            )

        # BERT
        if "bert" in results:
            bp, br, bf = results["bert"][i]
            print(f"[BERT] P:{bp:.4f}, R:{br:.4f}, F:{bf:.4f}")

        # G-EVAL
        if "g-eval" in results:
            gscore = results["g-eval"][i]
            print(f"[G-EVAL] score={gscore:.4f}")


def print_averages(results, n_items):
    """
    전체 평균 스코어(ROUGE/BERT/G-EVAL)를 출력
    """
    print("\n===== Averages =====")

    # ROUGE 평균
    if "rouge" in results:
        rouge_list = results["rouge"]
        sums = {
            "r1_p": 0,
            "r1_r": 0,
            "r1_f": 0,
            "r2_p": 0,
            "r2_r": 0,
            "r2_f": 0,
            "rl_p": 0,
            "rl_r": 0,
            "rl_f": 0,
        }
        for item in rouge_list:
            p, r, f = item["rouge1"]
            sums["r1_p"] += p
            sums["r1_r"] += r
            sums["r1_f"] += f

            p, r, f = item["rouge2"]
            sums["r2_p"] += p
            sums["r2_r"] += r
            sums["r2_f"] += f

            p, r, f = item["rougeL"]
            sums["rl_p"] += p
            sums["rl_r"] += r
            sums["rl_f"] += f

        print("\n[ROUGE Avg]")
        print(
            f"  ROUGE-1  P: {sums['r1_p']/n_items:.4f}, "
            f"R: {sums['r1_r']/n_items:.4f}, "
            f"F1: {sums['r1_f']/n_items:.4f}"
        )
        print(
            f"  ROUGE-2  P: {sums['r2_p']/n_items:.4f}, "
            f"R: {sums['r2_r']/n_items:.4f}, "
            f"F1: {sums['r2_f']/n_items:.4f}"
        )
        print(
            f"  ROUGE-L  P: {sums['rl_p']/n_items:.4f}, "
            f"R: {sums['rl_r']/n_items:.4f}, "
            f"F1: {sums['rl_f']/n_items:.4f}"
        )

    # BERTScore 평균
    if "bert" in results:
        bert_list = results["bert"]
        p_sum = r_sum = f_sum = 0.0
        for p, r, f in bert_list:
            p_sum += p
            r_sum += r
            f_sum += f
        print("\n[BERT Avg]")
        print(f"  Precision: {p_sum/n_items:.4f}, " f"Recall: {r_sum/n_items:.4f}, " f"F1: {f_sum/n_items:.4f}")

    # G-EVAL 평균
    if "g-eval" in results:
        geval_list = results["g-eval"]
        avg_score = sum(geval_list) / n_items
        print("\n[G-EVAL Avg]")
        print(f"  Score: {avg_score:.4f}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="eval_config.yml", help="Path to YAML config file")
    args = parser.parse_args()

    # 1) YAML 설정 로드
    config = load_config(args.config)
    csv_file = config.get("csv_file", None)
    metrics = config.get("metrics", [])

    if not csv_file:
        raise ValueError("config.yml에 csv_file 경로가 지정되지 않았습니다.")

    # 2) CSV 로드
    source_texts, summarized_texts, gold_texts = load_data(csv_file)

    # 3) 길이 검사
    validate_data_lengths(metrics, source_texts, summarized_texts, gold_texts)

    # 4) 메트릭 계산
    results = compute_metrics(config, source_texts, summarized_texts, gold_texts)

    # 5) 결과 출력
    print("===== Evaluation Results =====")
    print_per_item_scores(results, source_texts, summarized_texts, gold_texts)
    print_averages(results, len(summarized_texts))


if __name__ == "__main__":
    main()
