from rouge_score import rouge_scorer
import argparse
import torch
from bert_score import score

# Metrics Calculator Base Class
class MetricsCalculator:
    def calculate(self, gold, generated):
        raise NotImplementedError("Subclasses should implement this method")

# ROUGE Calculator Class
class RougeCalculator(MetricsCalculator):
    def __init__(self):
        self.scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)

    def calculate(self, gold, generated):
        scores = self.scorer.score(gold, generated)
        return {
            "ROUGE-1": {
                "precision": scores["rouge1"].precision,
                "recall": scores["rouge1"].recall,
                "f1": scores["rouge1"].fmeasure
            },
            "ROUGE-2": {
                "precision": scores["rouge2"].precision,
                "recall": scores["rouge2"].recall,
                "f1": scores["rouge2"].fmeasure
            },
            "ROUGE-L": {
                "precision": scores["rougeL"].precision,
                "recall": scores["rougeL"].recall,
                "f1": scores["rougeL"].fmeasure
            }
        }

class BERTScoreCalculator(MetricsCalculator):
    def __init__(self, model_type='distilbert-base-uncased', device=None):
        self.model_type = model_type
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
    
    def calculate(self, gold, generated):
        """
        gold: 정답 요약 텍스트 (문자열)
        generated: 생성된 요약 텍스트 (문자열)

        BERTScore는 일반적으로 여러 문장 쌍의 리스트를 받도록 설계되었으나,
        여기서는 단일 pair(gold, generated)에 대해서만 호출한다고 가정하고 작성합니다.
        """
        # bert_score.score 함수는 리스트를 인자로 받으므로, 단일 문장도 리스트로 감싸줍니다.
        P, R, F1 = score(
            cands=[generated], 
            refs=[gold], 
            model_type=self.model_type, 
            device=self.device
        )
        # 반환된 P, R, F1은 텐서이므로, item()으로 값을 뽑고 float로 변환합니다.
        return {
            "precision": float(P[0]),
            "recall": float(R[0]),
            "f1": float(F1[0])
        }


# Metrics Manager Class
class MetricsManager:
    def __init__(self):
        self.calculators = {}

    def register_calculator(self, name, calculator):
        if not issubclass(type(calculator), MetricsCalculator):
            raise ValueError("Calculator must be a subclass of MetricsCalculator")
        self.calculators[name] = calculator

    def calculate_metrics(self, gold, generated):
        results = {}
        for name, calculator in self.calculators.items():
            results[name] = calculator.calculate(gold, generated)
        return results

# Main function to parse inputs and calculate metrics
def main():
    parser = argparse.ArgumentParser(description="Calculate evaluation metrics for generated summaries.")
    parser.add_argument("--gold", required=True, help="Path to the gold (reference) summaries file.")
    parser.add_argument("--generated", required=True, help="Path to the generated summaries file.")

    args = parser.parse_args()

    # Read gold summaries
    with open(args.gold, "r", encoding="utf-8") as gold_file:
        gold_texts = [line.strip() for line in gold_file]

    # Read generated summaries
    with open(args.generated, "r", encoding="utf-8") as generated_file:
        generated_texts = [line.strip() for line in generated_file]

    # Check if both files have the same number of lines
    if len(gold_texts) != len(generated_texts):
        print("Error: The number of lines in the gold and generated files must match.")
        return

    # Initialize Metrics Manager and Register Calculators
    metrics_manager = MetricsManager()
    metrics_manager.register_calculator("ROUGE", RougeCalculator())

    # BERTScoreCalculator 등록
    metrics_manager.register_calculator("BERTScore", BERTScoreCalculator())

    # Calculate metrics for each pair
    overall_scores = {metric: [] for metric in metrics_manager.calculators.keys()}

    for gold, generated in zip(gold_texts, generated_texts):
        metrics = metrics_manager.calculate_metrics(gold, generated)
        for metric, scores in metrics.items():
            overall_scores[metric].append(scores)

    # Compute average scores for each metric
    avg_scores = {}
    for metric, score_list in overall_scores.items():
        # ROUGE는 dict(ROUGE-1, ROUGE-2, ROUGE-L), BERTScore는 dict(precision, recall, f1)
        # 구조가 다를 수 있으니 분기 처리가 필요할 수 있음
        if metric == "ROUGE":
            # 기존 ROUGE 평균 계산 로직
            avg_scores[metric] = {}
            for key in score_list[0]:  # "ROUGE-1", "ROUGE-2", "ROUGE-L" 등
                avg_scores[metric][key] = {
                    "precision": sum(s[key]["precision"] for s in score_list) / len(score_list),
                    "recall": sum(s[key]["recall"] for s in score_list) / len(score_list),
                    "f1": sum(s[key]["f1"] for s in score_list) / len(score_list),
                }
        elif metric == "BERTScore":
            # BERTScore는 dict(precision, recall, f1) 형태
            precision = sum(s["precision"] for s in score_list) / len(score_list)
            recall = sum(s["recall"] for s in score_list) / len(score_list)
            f1 = sum(s["f1"] for s in score_list) / len(score_list)
            avg_scores[metric] = {
                "precision": precision,
                "recall": recall,
                "f1": f1
            }
        else:
            # 혹은 다른 메트릭이 추가되었을 경우에 대비
            pass

    # Print average scores
    print("Average Scores:")
    for metric, scores in avg_scores.items():
        print(f"\n{metric}:")
        if metric == "ROUGE":
            for key, values in scores.items():
                print(f"  {key} - Precision: {values['precision']:.4f}, Recall: {values['recall']:.4f}, F1: {values['f1']:.4f}")
        elif metric == "BERTScore":
            print(f"  Precision: {scores['precision']:.4f}, Recall: {scores['recall']:.4f}, F1: {scores['f1']:.4f}")
            
if __name__ == "__main__":
    main()
