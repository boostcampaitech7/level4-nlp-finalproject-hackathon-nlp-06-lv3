import math
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import chi2_contingency, entropy
from sklearn.metrics import confusion_matrix


class MetricCalculator:
    """
    - 2×2 혼동행렬 계산 및 시각화
    - 멀티클래스 지표(Entropy, Diversity, Chi-Square, Accuracy, Cramer's V) 계산
    - Ground Truth vs Inference 상관계수 계산
    """

    @staticmethod
    def compute_metrics(results: list, ground_truth: str):
        """
        (1) Entropy, (2) Diversity Index, (3) Chi-Square p-value, (4) Accuracy, (5) Cramer's V
           을 멀티클래스 관점에서 계산.
        """
        value_counts = pd.Series(results).value_counts(normalize=True)
        entropy_value = entropy(value_counts)  # (1)
        diversity_index = len(value_counts) / len(results)  # (2)

        # 멀티클래스 혼동행렬
        unique_labels = sorted(set([ground_truth] + results))
        true_arr = [ground_truth] * len(results)
        conf_matrix = confusion_matrix(true_arr, results, labels=unique_labels)

        # chi-square (3)
        try:
            _, p_val, _, _ = chi2_contingency(conf_matrix)
        except ValueError:
            _, p_val = 0, 1

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
    def compute_binary_confusion_matrix(results: list, ground_truth: str):
        """
        - Positive: pred == ground_truth
        - Negative: pred != ground_truth
        - 2×2 강제 변환
        """
        binary_preds = ["Positive" if r == ground_truth else "Negative" for r in results]
        binary_true = ["Positive"] * len(results)

        labels_2class = ["Negative", "Positive"]
        conf_matrix = confusion_matrix(binary_true, binary_preds, labels=labels_2class)

        # 2×2 보정
        if conf_matrix.shape == (1, 1):
            conf_matrix = np.array([[conf_matrix[0, 0], 0], [0, 0]])
        elif conf_matrix.shape == (1, 2):
            conf_matrix = np.vstack([conf_matrix, [0, 0]])
        elif conf_matrix.shape == (2, 1):
            conf_matrix = np.hstack([conf_matrix, [[0], [0]]])

        return conf_matrix, labels_2class

    @staticmethod
    def plot_confusion_matrix(conf_matrix, labels, category):
        """
        2×2 혼동행렬 시각화 -> png 저장
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
            yticklabels=["False", "True"],
            ax=ax,
            linewidths=1,
            linecolor="black",
            cbar=True,
        )

        plt.xlabel("Predicted Labels")
        plt.ylabel("True Labels")
        plt.title(f"Confusion Matrix for {category}")

        save_path = os.path.join(output_dir, f"{category}_confusion_matrix.png")
        plt.savefig(save_path, bbox_inches="tight", dpi=300)
        plt.close()

        print(f"✅ Confusion Matrix 저장 완료: {save_path}")

    @staticmethod
    def compute_overall_accuracy(eval_df: pd.DataFrame, inference_count: int) -> float:
        """
        - 전체(row) 기준: inference 결과 중 ground_truth와 일치하는지
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
        Ground Truth별 그룹 후, 2×2 혼동행렬로 (TP+TN)/total 계산
        """
        cat_accuracy = {}

        grouped = eval_df.groupby("ground_truth")
        for gt, group in grouped:
            # 해당 GT 그룹 내 모든 inference 결과
            cat_results = group.iloc[:, 2:-5].values.flatten().tolist()

            cm_2x2, label2class = MetricCalculator.compute_binary_confusion_matrix(cat_results, gt)
            MetricCalculator.plot_confusion_matrix(cm_2x2, label2class, str(gt))
            cat_acc = cm_2x2.trace() / cm_2x2.sum() if cm_2x2.sum() else 0
            cat_accuracy[gt] = cat_acc

        return cat_accuracy

    @staticmethod
    def compute_correlation_with_gt(eval_df: pd.DataFrame, inference_count: int):
        """
        Ground Truth vs 각 inference_{i+1} 열에 대한 상관계수 (Pearson, Spearman)
        """
        inf_cols = [f"inference_{i+1}" for i in range(inference_count)]
        unique_cats = pd.unique(eval_df[["ground_truth"] + inf_cols].values.ravel()).tolist()
        unique_cats = sorted(unique_cats)
        cat_to_id = {cat: i for i, cat in enumerate(unique_cats)}

        # numeric 변환
        df_num = eval_df.copy()
        df_num["ground_truth_num"] = df_num["ground_truth"].map(cat_to_id)
        for col in inf_cols:
            df_num[col + "_num"] = df_num[col].map(cat_to_id)

        results = []  # [(pearson_1, spearman_1), ...]
        for i in range(inference_count):
            col_num = inf_cols[i] + "_num"
            gt_s = df_num["ground_truth_num"]
            inf_s = df_num[col_num]

            if gt_s.nunique() < 2 or inf_s.nunique() < 2:
                # 변동이 없는(상수) 열이면 corr 불가
                pearson_c = 0.0
                spearman_c = 0.0
            else:
                pearson_c = gt_s.corr(inf_s, method="pearson")
                spearman_c = gt_s.corr(inf_s, method="spearman")
                # NaN 방어
                pearson_c = pearson_c if not math.isnan(pearson_c) else 0.0
                spearman_c = spearman_c if not math.isnan(spearman_c) else 0.0

            results.append((pearson_c, spearman_c))

        return results

    @staticmethod
    def group_consistency_metrics(eval_df: pd.DataFrame, inference_count: int) -> pd.DataFrame:
        """
        Ground Truth별로 모은 뒤, 멀티클래스 지표(Entropy, Accuracy, 등)를 종합해 DataFrame화
        """
        if eval_df.empty:
            return pd.DataFrame()

        grouped_results = []
        grouped = eval_df.groupby("ground_truth")

        for gt, group_df in grouped:
            # 해당 GT 그룹 내 모든 inference 결과
            cat_results = group_df.iloc[:, 2:-5].values.flatten().tolist()

            (entropy_value, diversity_index, p_value, accuracy, _, _, c_v) = MetricCalculator.compute_metrics(
                cat_results, gt
            )

            grouped_results.append([gt, entropy_value, diversity_index, p_value, accuracy, c_v])

        columns = ["Ground Truth", "Entropy", "Diversity Index", "Chi-Square p-value", "Accuracy", "Cramer's V"]
        summary_df = pd.DataFrame(grouped_results, columns=columns)
        return summary_df
