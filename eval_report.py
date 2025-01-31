import argparse
import json

import torch
import yaml
from bert_score import score as bert_score
from dotenv import load_dotenv
from openai import OpenAI
from rouge_score import rouge_scorer

load_dotenv()
client = OpenAI()


def load_config(config_path):
    """
    주어진 경로의 YAML 파일을 로드해 dict 형태로 반환
    """
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_report_data(json_file):
    """
    JSON 파일 예시:
    [
      {
        "source": "이메일들의 concat 내용, <SEP>로 구분",
        "report": "최종 일일 보고서",
        "reference": "gold 요약(선택)"
      },
      ...
    ]
    """
    with open(json_file, "r", encoding="utf-8") as f:
        data_list = json.load(f)

    source_texts = []
    report_texts = []
    reference_texts = []

    for item in data_list:
        source_texts.append(item["source"])
        report_texts.append(item["report"])
        reference_texts.append(item.get("reference", None))  # 없을 경우 None

    return source_texts, report_texts, reference_texts


def calculate_rouge(gold_texts, generated_texts):
    """
    gold_texts, generated_texts: 각 샘플별 참조 / 생성 텍스트
    리턴: [{"rouge1":(p,r,f), "rouge2":(p,r,f), "rougeL":(p,r,f)}, ...]
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
    BERTScore 계산. 각 샘플별 (precision, recall, f1) 튜플 리스트 반환
    """
    if torch.backends.mps.is_available():
        device = "mps"
    elif torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"

    P, R, F1 = bert_score(cands=generated_texts, refs=gold_texts, model_type=model_type, device=device)
    results = []
    for i in range(len(gold_texts)):
        results.append((P[i].item(), R[i].item(), F1[i].item()))
    return results


def calculate_g_eval(source_texts, generated_texts, config):
    """
    G-EVAL(gold 없이도 평가 가능) - 7가지 관점(아래 aspects)에 대해 각각 OpenAI API로 점수를 얻음.

    반환 예시:
      [
        {
          "consistency": float,
          "coherence": float,
          "fluency": float,
          "relevance": float,
          "readability": float,
          "clearance": float,
          "practicality": float
        },
        ...
      ]
    """
    g_eval_config = config.get("g_eval", {})
    prompt_files = g_eval_config.get("prompts", {})
    model_name = g_eval_config.get("openai_model", "gpt-4")

    # 7개 평가 관점
    aspects = [
        "consistency",
        "coherence",
        "fluency",
        "relevance",
        "readability",
        "clearance",
        "practicality",
    ]

    all_scores = []
    for src, gen in zip(source_texts, generated_texts):
        aspect_scores = {}
        for aspect in aspects:
            prompt_file = prompt_files.get(aspect, None)
            if not prompt_file:
                # 해당 프롬프트 파일이 없으면 0점 처리
                aspect_scores[aspect] = 0.0
                continue

            # 프롬프트 불러오기
            with open(prompt_file, "r", encoding="utf-8") as f:
                base_prompt = f.read()

            # {{Document}} / {{Summary}} 등의 placeholder 치환
            cur_prompt = base_prompt.replace("{{Document}}", src).replace("{{Summary}}", gen)

            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "system", "content": cur_prompt}],
                    temperature=0.7,
                    max_tokens=50,
                    n=1,
                )
                gpt_text = response.choices[0].message.content.strip()
                score_value = float(gpt_text)  # 예: "3.5" → 3.5
                aspect_scores[aspect] = score_value
            except Exception as e:
                print(f"[Error in G-EVAL] aspect={aspect}, error={e}")
                aspect_scores[aspect] = 0.0

        all_scores.append(aspect_scores)

    return all_scores


def validate_data_lengths(metrics, source_texts, report_texts, reference_texts):
    """
    - ROUGE/BERT는 gold(reference)가 필요 (모두 None이면 안 됨)
    - G-EVAL은 source와 report만 있으면 됨
    """
    n_reports = len(report_texts)

    # ROUGE or BERT
    if ("rouge" in metrics) or ("bert" in metrics):
        # reference_texts 중 None이 있으면 문제가 됨
        if any(ref is None for ref in reference_texts):
            raise ValueError("ROUGE/BERT 평가에 필요한 reference(골드)가 없습니다.")
        if len(reference_texts) != n_reports:
            raise ValueError("reference 항목과 report 항목 개수가 일치하지 않습니다.")

    if "g-eval" in metrics:
        if len(source_texts) != n_reports:
            raise ValueError("source 항목과 report 항목 개수가 일치하지 않습니다.")


def compute_metrics(config, source_texts, report_texts, reference_texts):
    """
    설정(config)에 따라 ROUGE / BERT / G-EVAL 계산
    """
    metrics = config.get("metrics", [])
    results = {}

    # BERT 용 모델
    bert_model_type = config.get("bert_model", "distilbert-base-uncased")

    # ROUGE
    if "rouge" in metrics:
        rouge_res = calculate_rouge(reference_texts, report_texts)
        results["rouge"] = rouge_res

    # BERT
    if "bert" in metrics:
        bert_res = calculate_bert(reference_texts, report_texts, model_type=bert_model_type)
        results["bert"] = bert_res

    # G-EVAL
    if "g-eval" in metrics:
        geval_res = calculate_g_eval(source_texts, report_texts, config)
        results["g-eval"] = geval_res

    return results


def print_per_item_scores(results, source_texts, report_texts, reference_texts):
    """
    각 샘플별 점수를 출력
    """
    n_items = len(report_texts)
    for i in range(n_items):
        print(f"\n--- Report Sample {i+1} ---")

        # ROUGE
        if "rouge" in results:
            ritem = results["rouge"][i]
            r1p, r1r, r1f = ritem["rouge1"]
            r2p, r2r, r2f = ritem["rouge2"]
            rlp, rlr, rlf = ritem["rougeL"]
            print(
                f"[ROUGE] "
                f"R1=(P:{r1p:.4f},R:{r1r:.4f},F:{r1f:.4f}), "
                f"R2=(P:{r2p:.4f},R:{r2r:.4f},F:{r2f:.4f}), "
                f"RL=(P:{rlp:.4f},R:{rlr:.4f},F:{rlf:.4f})"
            )

        # BERT
        if "bert" in results:
            bp, br, bf = results["bert"][i]
            print(f"[BERT] P:{bp:.4f}, R:{br:.4f}, F:{bf:.4f}")

        # G-EVAL
        if "g-eval" in results:
            gitem = results["g-eval"][i]
            # 7개 점수를 순서대로
            print(
                "[G-EVAL] "
                f"consistency={gitem['consistency']:.4f}, "
                f"coherence={gitem['coherence']:.4f}, "
                f"fluency={gitem['fluency']:.4f}, "
                f"relevance={gitem['relevance']:.4f}, "
                f"readability={gitem['readability']:.4f}, "
                f"clearance={gitem['clearance']:.4f}, "
                f"practicality={gitem['practicality']:.4f}"
            )


def print_averages(results, n_items):
    """
    전체 평균 스코어를 출력
    """
    print("\n===== Averages =====")

    # ROUGE 평균
    if "rouge" in results:
        rouge_list = results["rouge"]
        sums = {
            "r1_p": 0.0,
            "r1_r": 0.0,
            "r1_f": 0.0,
            "r2_p": 0.0,
            "r2_r": 0.0,
            "r2_f": 0.0,
            "rl_p": 0.0,
            "rl_r": 0.0,
            "rl_f": 0.0,
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
            f"  ROUGE-1: P={sums['r1_p']/n_items:.4f}, "
            f"R={sums['r1_r']/n_items:.4f}, "
            f"F={sums['r1_f']/n_items:.4f}"
        )
        print(
            f"  ROUGE-2: P={sums['r2_p']/n_items:.4f}, "
            f"R={sums['r2_r']/n_items:.4f}, "
            f"F={sums['r2_f']/n_items:.4f}"
        )
        print(
            f"  ROUGE-L: P={sums['rl_p']/n_items:.4f}, "
            f"R={sums['rl_r']/n_items:.4f}, "
            f"F={sums['rl_f']/n_items:.4f}"
        )

    # BERT 평균
    if "bert" in results:
        bert_list = results["bert"]
        p_sum = r_sum = f_sum = 0.0
        for p, r, f in bert_list:
            p_sum += p
            r_sum += r
            f_sum += f
        print("\n[BERT Avg]")
        print(f"  Precision={p_sum/n_items:.4f}, " f"Recall={r_sum/n_items:.4f}, " f"F1={f_sum/n_items:.4f}")

    # G-EVAL 평균 (7개 측면)
    if "g-eval" in results:
        geval_list = results["g-eval"]
        con_sum = coh_sum = flu_sum = rel_sum = 0.0
        read_sum = clear_sum = prac_sum = 0.0

        for gdict in geval_list:
            con_sum += gdict["consistency"]
            coh_sum += gdict["coherence"]
            flu_sum += gdict["fluency"]
            rel_sum += gdict["relevance"]
            read_sum += gdict["readability"]
            clear_sum += gdict["clearance"]
            prac_sum += gdict["practicality"]

        print("\n[G-EVAL Avg]")
        print(
            f"  consistency={con_sum/n_items:.4f}, "
            f"coherence={coh_sum/n_items:.4f}, "
            f"fluency={flu_sum/n_items:.4f}, "
            f"relevance={rel_sum/n_items:.4f}, "
            f"readability={read_sum/n_items:.4f}, "
            f"clearance={clear_sum/n_items:.4f}, "
            f"practicality={prac_sum/n_items:.4f}"
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="eval_config.yml", help="Path to YAML config file")
    args = parser.parse_args()

    # 1) 설정 파일 로드
    config = load_config(args.config)

    json_file = config.get("json_file", None)

    if not json_file:
        raise ValueError("config.yml에 json_file 경로가 지정되지 않았습니다.")

    # 2) JSON 로드
    source_texts, report_texts, reference_texts = load_report_data(json_file)

    # 3) 데이터 길이 검사
    validate_data_lengths(config.get("metrics", []), source_texts, report_texts, reference_texts)

    # 4) 메트릭 계산
    results = compute_metrics(config, source_texts, report_texts, reference_texts)

    # 5) 결과 출력
    print("===== Report Evaluation Results =====")
    print_per_item_scores(results, source_texts, report_texts, reference_texts)
    print_averages(results, len(report_texts))


if __name__ == "__main__":
    main()
