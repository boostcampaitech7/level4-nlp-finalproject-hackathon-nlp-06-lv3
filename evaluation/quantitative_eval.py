import torch
from bert_score import score as bert_score
from rouge_score import rouge_scorer


def calculate_rouge(gold_texts, generated_texts):
    """
    gold_texts, generated_texts: 참조 텍스트와 생성된 요약
    리턴: [{"rouge1":(p,r,f), "rouge2":(p,r,f), "rougeL":(p,r,f)}, ...]
    """
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    results = []

    for gold, gen in zip(gold_texts, generated_texts):
        scores = scorer.score(gold, gen)
        item = {
            "rouge1": (scores["rouge1"].precision, scores["rouge1"].recall, scores["rouge1"].fmeasure),
            "rouge2": (scores["rouge2"].precision, scores["rouge2"].recall, scores["rouge2"].fmeasure),
            "rougeL": (scores["rougeL"].precision, scores["rougeL"].recall, scores["rougeL"].fmeasure),
        }
        results.append(item)
    return results


def calculate_bert(gold_texts, generated_texts, model_type="distilbert-base-uncased"):
    """
    BERTScore를 한 번에 계산 → 각 샘플별 (p, r, f) 튜플 리스트로 반환
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
