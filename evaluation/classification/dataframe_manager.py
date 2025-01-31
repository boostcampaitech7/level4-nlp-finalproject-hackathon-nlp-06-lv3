import os

import pandas as pd

from .metric_calculator import MetricCalculator


class DataFrameManager:
    """
    분류 결과(메일 ID, Ground Truth, N회차 Inference 등)를 관리/저장하고,
    MetricCalculator를 호출해 평가 지표를 계산하는 책임.
    """

    def __init__(self, inference_count: int):
        self.inference_count = inference_count
        self.output_dir = "evaluation/classification"
        os.makedirs(self.output_dir, exist_ok=True)
        self.csv_file_path = os.path.join(self.output_dir, "labeled.csv")

        self.columns = (
            ["mail_id", "ground_truth"]
            + [f"inference_{i+1}" for i in range(inference_count)]
            + ["entropy", "diversity_index", "chi_square_p_value", "accuracy", "cramers_v"]
        )

        if os.path.exists(self.csv_file_path):
            self.eval_df = pd.read_csv(self.csv_file_path)
            print(f"📄 기존 평가 데이터 로드 완료: {self.eval_df.shape[0]}개의 데이터")
        else:
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

        # metric 계산
        (entropy_val, diversity_val, p_val, acc_val, _, _, c_v) = MetricCalculator.compute_metrics(
            results, ground_truth
        )

        new_row = pd.DataFrame(
            [[mail_id, ground_truth] + results + [entropy_val, diversity_val, p_val, acc_val, c_v]],
            columns=self.columns,
        )
        self.eval_df = pd.concat([self.eval_df, new_row], ignore_index=True)
        self.eval_df.to_csv(self.csv_file_path, index=False)

    def print_df(self):
        """
        최종 결과를 출력:
          1) Correctness(카테고리별 2×2 혼동행렬, 전체/카테고리별 정확도, GT vs Inference 상관계수)
          2) Consistency(Ground Truth 별 요약된 메트릭)
        """
        if self.eval_df.empty:
            print("⚠️ 저장된 평가 데이터가 없습니다.")
            return
        self._print_correctness()

        self._print_consistency()

    def _print_correctness(self):
        """
        Correctness:
         - 카테고리별(ground_truth별) 2×2 혼동행렬 시각화
         - 전체 정확도, 카테고리별 정확도
         - Ground Truth vs Inference_i 상관계수(회차별)
        """
        # (1) 전체 정확도
        overall_acc = MetricCalculator.compute_overall_accuracy(self.eval_df, self.inference_count)

        # (2) 카테고리별 2×2 혼동행렬 & 정확도
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
