from rouge_score import rouge_scorer
import argparse

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

    # Calculate metrics for each pair
    overall_scores = {metric: [] for metric in metrics_manager.calculators.keys()}

    for gold, generated in zip(gold_texts, generated_texts):
        metrics = metrics_manager.calculate_metrics(gold, generated)
        for metric, scores in metrics.items():
            overall_scores[metric].append(scores)

    # Compute average scores for each metric
    avg_scores = {}
    for metric, score_list in overall_scores.items():
        avg_scores[metric] = {}
        for key in score_list[0]:  # "ROUGE-1", "ROUGE-2", "ROUGE-L" etc.
            avg_scores[metric][key] = {
                "precision": sum(s[key]["precision"] for s in score_list) / len(score_list),
                "recall": sum(s[key]["recall"] for s in score_list) / len(score_list),
                "f1": sum(s[key]["f1"] for s in score_list) / len(score_list),
            }

    # Print average scores
    print("Average Scores:")
    for metric, scores in avg_scores.items():
        print(f"\n{metric}:")
        for key, values in scores.items():
            print(f"  {key} - Precision: {values['precision']:.4f}, Recall: {values['recall']:.4f}, F1: {values['f1']:.4f}")

if __name__ == "__main__":
    main()
