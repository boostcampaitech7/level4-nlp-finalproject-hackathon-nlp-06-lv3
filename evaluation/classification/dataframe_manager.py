import pandas as pd

from evaluation.classification.metric_calculator import MetricCalculator


class DataFrameManager:
    """
    분류 결과(메일 ID, Ground Truth, N회차 Inference 등)를 관리/저장하고,
    MetricCalculator를 호출해 평가 지표를 계산하는 책임.
    """

    def __init__(self, inference_count: int, classification_type: str):
        self.inference_count = inference_count
        self.classification_type = classification_type

        self.columns = (
            ["mail_id", "ground_truth"]
            + [f"inference_{i+1}" for i in range(inference_count)]
            + ["entropy", "diversity_index", "chi_square_p_value", "accuracy", "cramers_v"]
        )
        self.ground_truth_df = pd.read_csv("evaluation/classification/ground_truth.csv", index_col="mail_id")

        self.eval_df = pd.DataFrame(columns=self.columns)

    def update_eval_df(self, mail_id: str, results: list, ground_truth: str):
        """
        1) 메일 ID 중복 체크
        2) 메트릭(Entropy, Diversity, p-value, Accuracy, Cramer's V) 계산
        3) CSV에 병합 저장
        """
        # 이미 처리된 메일인지 확인 + 모든 inference 칼럼이 채워졌는지 확인
        if mail_id in self.eval_df["mail_id"].values:
            existing = self.eval_df[self.eval_df["mail_id"] == mail_id]
            if existing.iloc[:, 2:-5].notna().all(axis=None):
                return

        # metric 계산 (메일 단위로 Entropy, Diversity 등만 구함)
        (entropy_val, diversity_val, p_val, acc_val, _, _, c_v) = MetricCalculator.compute_metrics(
            results, ground_truth
        )

        new_row = pd.DataFrame(
            [[mail_id, ground_truth] + results + [entropy_val, diversity_val, p_val, acc_val, c_v]],
            columns=self.columns,
        )

        if self.eval_df.empty:
            self.eval_df = new_row.copy()
        else:
            self.eval_df = pd.concat([self.eval_df, new_row], ignore_index=True)

    def print_df(self):
        """
        최종 결과를 출력:
          1) Correctness(카테고리별 2×2 Confusion Matrix, 전체/카테고리별 정확도, GT vs Inference 상관계수)
          2) Consistency(Ground Truth 별 요약된 메트릭)
          3) 전체 데이터셋 대상 멀티클래스 Confusion Matrix
        """
        if self.eval_df.empty:
            print("⚠️ 저장된 평가 데이터가 없습니다.")
            return

        self._print_correctness()
        self._print_consistency()
        self._print_multiclass_confusion_matrix()

    def _print_correctness(self):
        """
        Correctness:
         - 카테고리별(ground_truth별) 2×2 Confusion Matrix 시각화
         - 전체 정확도, 카테고리별 정확도
        """
        # (1) 전체 정확도
        overall_acc = MetricCalculator.compute_overall_accuracy(self.eval_df, self.inference_count)

        # (2) 카테고리별 2×2 Confusion Matrix & 정확도
        cat_accuracy_dict = MetricCalculator.compute_category_accuracy_2x2(self.eval_df, self.inference_count)

        print("\nCorrectness")
        print(f"🎯 전체 정확도: {overall_acc:.4f}")
        for gt, acc in cat_accuracy_dict.items():
            print(f"🎯 {gt} 정확도: {acc:.4f}")
        print()

    def _print_consistency(self):
        """
        Consistency:
         - Ground Truth 별 Entropy, Diversity Index, Chi-Square p-value, Accuracy, Cramer's V
        """
        summary_df = MetricCalculator.group_consistency_metrics(self.eval_df, self.inference_count)
        print("Consistency")
        print("📊 Ground Truth 별 요약된 평가 메트릭")
        print(summary_df)
        summary_df.to_csv(f"evaluation/classification/{self.classification_type}_consistency.csv")

    def _print_multiclass_confusion_matrix(self):
        """
        전체 데이터셋을 대상으로 한 멀티클래스 Confusion Matrix 출력.
        (inference_count회 추론 모두를 '샘플'로 취급)
        """
        conf_matrix, label_list = MetricCalculator.compute_overall_multiclass_confusion_matrix(
            self.eval_df, self.inference_count
        )
        print("\n=== Overall Multiclass Confusion Matrix ===")
        print("Labels:", label_list)
        print(conf_matrix)
        print("===========================================\n")
