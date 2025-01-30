import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import chi2_contingency, entropy
from sklearn.metrics import confusion_matrix


class MetricCalculator:
    """Consistency 및 Correctness 평가를 수행하는 클래스."""

    @staticmethod
    def compute_metrics(results: list, ground_truth: str):
        """
        주어진 결과에 대해 Consistency 및 Correctness 평가 수행.

        Args:
            results (list): 분류 모델의 예측 결과 리스트.
            ground_truth (str): 실제 정답 데이터 (단일 값).

        Returns:
            tuple: (entropy_value, diversity_index, p_value, accuracy, conf_matrix, labels)
        """
        value_counts = pd.Series(results).value_counts(normalize=True)
        entropy_value = entropy(value_counts)
        diversity_index = len(value_counts) / len(results)
        chi2, p_value, _, _ = chi2_contingency(pd.crosstab(pd.Series(results), pd.Series(results)))

        true_labels_flat = [ground_truth] * len(results)
        results_flat = results

        unique_labels = sorted(list(set([ground_truth] + results)))  # 항상 Ground Truth 포함

        # Confusion Matrix 계산 (binary 형태 강제)
        conf_matrix = confusion_matrix(true_labels_flat, results_flat, labels=unique_labels)

        # 2×2 Confusion Matrix 강제 변환
        if conf_matrix.shape == (1, 1):  # 한 개의 클래스만 있는 경우
            conf_matrix = np.array([[conf_matrix[0, 0], 0], [0, 0]])
        elif conf_matrix.shape == (1, 2):  # 한 개의 행만 있는 경우
            conf_matrix = np.vstack([conf_matrix, [0, 0]])
        elif conf_matrix.shape == (2, 1):  # 한 개의 열만 있는 경우
            conf_matrix = np.hstack([conf_matrix, [[0], [0]]])

        accuracy = np.trace(conf_matrix) / np.sum(conf_matrix) if np.sum(conf_matrix) > 0 else 0

        return entropy_value, diversity_index, p_value, accuracy, conf_matrix, unique_labels

    @staticmethod
    def plot_confusion_matrix(conf_matrix, labels, category):
        """
        2×2 Confusion Matrix를 저장 (텍스트 없음).

        Args:
            conf_matrix (np.array): Confusion Matrix 데이터.
            labels (list): Confusion Matrix의 라벨.
            category (str): 현재 Ground Truth 카테고리.
        """
        output_dir = "evaluation/classification/figure"
        os.makedirs(output_dir, exist_ok=True)  # 디렉토리 생성 (없으면 자동 생성)

        fig, ax = plt.subplots(figsize=(5, 4))
        sns.heatmap(
            conf_matrix,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=["Negative", "Positive"],
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
        plt.savefig(save_path, bbox_inches="tight", dpi=300)  # 파일로 저장
        plt.close()  # 그래프 닫기

        print(f"✅ Confusion Matrix 저장 완료: {save_path}")
