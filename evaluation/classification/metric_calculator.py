import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import chi2_contingency, entropy
from sklearn.metrics import confusion_matrix


class MetricCalculator:
    """
    - 2×2 Confusion Matrix 계산 및 시각화
    - 멀티클래스 지표(Entropy, Diversity, Chi-Square, Accuracy, Cramer's V) 계산
    - Ground Truth vs Inference 상관계수 계산
    """

    @staticmethod
    def compute_metrics(results: list, ground_truth: str):
        """
        (1) Entropy, (2) Diversity Index, (3) Chi-Square p-value, (4) Accuracy, (5) Cramer's V
           을 '메일 단위'로 계산 (ground_truth 1개에 대해 여러 번 추론한 results).
        """
        value_counts = pd.Series(results).value_counts(normalize=True)
        entropy_value = entropy(value_counts)  # (1)
        diversity_index = len(value_counts) / len(results) if len(results) > 0 else 0  # (2)

        # 멀티클래스 Confusion Matrix
        unique_labels = sorted(set([ground_truth] + results))
        true_arr = [ground_truth] * len(results)
        conf_matrix = confusion_matrix(true_arr, results, labels=unique_labels)

        # chi-square (3)
        try:
            _, p_val, _, _ = chi2_contingency(conf_matrix)
        except ValueError:
            # 기대빈도가 0이거나 카테고리가 1개뿐이면 오류 => p_val=1
            p_val = 1

        # accuracy (4) = diagonal / total
        total = conf_matrix.sum()
        accuracy = np.trace(conf_matrix) / total if total > 0 else 0

        # Cramer's V (5)
        c_v = MetricCalculator.cramers_v(conf_matrix)

        return entropy_value, diversity_index, p_val, accuracy, conf_matrix, unique_labels, c_v

    @staticmethod
    def cramers_v(conf_matrix: np.ndarray) -> float:
        """멀티클래스용 Cramer's V."""
        try:
            chi2, _, _, _ = chi2_contingency(conf_matrix)
        except ValueError:
            return 0.0

        n = conf_matrix.sum()
        k = min(conf_matrix.shape)
        if n == 0 or (k - 1) == 0:
            return 0.0

        return float(np.sqrt(chi2 / (n * (k - 1))))

    @staticmethod
    def compute_binary_confusion_matrix(eval_df: pd.DataFrame, category: str, inference_count: int):
        """
        - 전체 데이터셋을 대상으로, 'category' vs. 'not-category'로 2×2 Confusion Matrix 계산.
        - inference_count 회 각각을 샘플로 본다.
        """
        all_predictions = []
        all_ground_truths = []

        for _, row in eval_df.iterrows():
            gt = row["ground_truth"]
            for i in range(inference_count):
                pred = row[f"inference_{i+1}"]
                # ground_truth가 category이면 Positive, 아니면 Negative
                all_ground_truths.append("Positive" if gt == category else "Negative")
                # 예측이 category이면 Positive, 아니면 Negative
                all_predictions.append("Positive" if pred == category else "Negative")

        labels_2class = ["Negative", "Positive"]
        conf_matrix = confusion_matrix(all_ground_truths, all_predictions, labels=labels_2class)
        return conf_matrix, labels_2class

    @staticmethod
    def plot_confusion_matrix(conf_matrix, labels, category):
        """
        2×2 Confusion Matrix 시각화 -> png 저장
        """
        output_dir = "evaluation/classification/figure"
        os.makedirs(output_dir, exist_ok=True)

        fig, ax = plt.subplots(figsize=(5, 4))
        sns.heatmap(
            conf_matrix,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=labels,
            yticklabels=labels,
            ax=ax,
            linewidths=1,
            linecolor="black",
            cbar=True,
        )

        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        plt.title(f"2x2 Confusion Matrix for '{category}'")

        save_path = os.path.join(output_dir, f"{category}_confusion_matrix.png")
        plt.savefig(save_path, bbox_inches="tight", dpi=300)
        plt.close()

        print(f"✅ Confusion Matrix 저장 완료: {save_path}")

    @staticmethod
    def compute_overall_accuracy(eval_df: pd.DataFrame, inference_count: int) -> float:
        """
        전체 데이터셋에 대해:
        - 각 row(메일)에 대해 inference_count회 한 예측을 전부 샘플로 보고,
        - ground_truth와 일치하는지 여부를 총합으로 계산.
        """
        inf_cols = [f"inference_{i+1}" for i in range(inference_count)]
        total_correct = 0
        total_count = 0

        for _, row in eval_df.iterrows():
            gt = row["ground_truth"]
            for col in inf_cols:
                pred = row[col]
                total_count += 1
                if pred == gt:
                    total_correct += 1

        return total_correct / total_count if total_count > 0 else 0

    @staticmethod
    def compute_category_accuracy_2x2(eval_df: pd.DataFrame, inference_count: int):
        """
        - 전체 데이터셋을 대상으로, 카테고리마다 2×2 confusion matrix 계산.
        - (TP+TN)/total 로 Accuracy 계산 및 그림 저장.
        """
        cat_accuracy = {}
        unique_cats = sorted(eval_df["ground_truth"].unique())

        for category in unique_cats:
            cm_2x2, label2class = MetricCalculator.compute_binary_confusion_matrix(eval_df, category, inference_count)
            MetricCalculator.plot_confusion_matrix(cm_2x2, label2class, str(category))

            total = cm_2x2.sum()
            cat_acc = cm_2x2.trace() / total if total else 0
            cat_accuracy[category] = cat_acc

        return cat_accuracy

    @staticmethod
    def group_consistency_metrics(eval_df: pd.DataFrame, inference_count: int) -> pd.DataFrame:
        """
        Ground Truth별로 모아서, 각 그룹 내 (메일별) inference 결과를 합쳐
        Entropy, Diversity, p-value, Accuracy, Cramer's V를 계산.
        """
        if eval_df.empty:
            return pd.DataFrame()

        grouped_results = []
        grouped = eval_df.groupby("ground_truth")

        for gt, group_df in grouped:
            # 해당 GT 그룹 내 '여러 메일의 inference 결과'를 하나로 통합
            cat_results = group_df.iloc[:, 2:-5].values.flatten().tolist()
            (entropy_value, diversity_index, p_value, accuracy, _, _, c_v) = MetricCalculator.compute_metrics(
                cat_results, gt
            )
            grouped_results.append([gt, entropy_value, diversity_index, p_value, accuracy, c_v])

        columns = ["Ground Truth", "Entropy", "Diversity Index", "Chi-Square p-value", "Accuracy", "Cramer's V"]
        summary_df = pd.DataFrame(grouped_results, columns=columns)
        return summary_df

    @staticmethod
    def compute_overall_multiclass_confusion_matrix(eval_df: pd.DataFrame, inference_count: int):
        """
        전체 데이터셋에 대해 (메일 × inference_count) 샘플을 전부 모아 멀티클래스 Confusion Matrix 생성
        """
        all_preds = []
        all_gts = []

        for _, row in eval_df.iterrows():
            gt = row["ground_truth"]
            for i in range(inference_count):
                pred = row[f"inference_{i+1}"]
                all_preds.append(pred)
                all_gts.append(gt)

        label_list = sorted(set(all_preds + all_gts))
        conf_matrix = confusion_matrix(all_gts, all_preds, labels=label_list)
        return conf_matrix, label_list
