import os

import pandas as pd

from .metric_calculator import MetricCalculator


class DataFrameManager:
    """
    평가 데이터 프레임을 관리하고, 분류 모델 평가 결과를 저장 및 분석하는 클래스.

    Args:
        inference_count (int): 동일한 입력 데이터에 대해 수행할 추론 횟수.
    """

    def __init__(self, inference_count: int):
        self.output_dir = "evaluation/classification/label_data"
        os.makedirs(self.output_dir, exist_ok=True)
        self.csv_file_path = os.path.join(self.output_dir, "labeled.csv")

        # 평가 데이터프레임의 컬럼 정의
        self.columns = (
            ["mail_id", "ground_truth"]
            + [f"inference_{i+1}" for i in range(inference_count)]
            + ["entropy", "diversity_index", "chi_square_p_value", "accuracy"]
        )

        # 기존 데이터가 존재하면 로드, 없으면 빈 데이터프레임 생성
        if os.path.exists(self.csv_file_path):
            self.eval_df = pd.read_csv(self.csv_file_path)
            print(f"📄 기존 평가 데이터 로드 완료: {self.eval_df.shape[0]}개의 데이터")
        else:
            self.eval_df = pd.DataFrame(columns=self.columns)

    def update_eval_df(self, mail_id: str, results: list, ground_truth: str):
        """
        평가 데이터프레임을 업데이트하고, 결과를 CSV 파일로 저장합니다.

        이미 처리된 메일이거나, 기존 평가 데이터가 완전할 경우(모든 inference_n 칼럼이 채워진 경우) 건너뜁니다.

        Args:
            mail_id (str): 메일의 고유 ID.
            results (list): 분류 결과 리스트.
            ground_truth (str): 해당 메일의 정답(ground truth).
        """
        # 기존 데이터에서 해당 mail_id가 있는지 확인
        if mail_id in self.eval_df["mail_id"].values:
            existing_entry = self.eval_df[self.eval_df["mail_id"] == mail_id]

            # 기존 결과에서 inference 값이 전부 채워져 있는지 확인
            if existing_entry.iloc[:, 2:-4].notna().all(axis=None):
                return

        # Consistency 및 Correctness 지표 계산
        entropy_value, diversity_index, p_value, accuracy = MetricCalculator.compute_metrics(results, ground_truth)

        # 새로운 평가 결과 추가
        new_entry = pd.DataFrame(
            [[mail_id, ground_truth] + results + [entropy_value, diversity_index, p_value, accuracy]],
            columns=self.columns,
        )

        # 기존 데이터와 병합
        self.eval_df = pd.concat([self.eval_df, new_entry], ignore_index=True)

        # 평가 결과를 CSV 파일로 저장
        self.eval_df.to_csv(self.csv_file_path, index=False)

    def group_and_compute_metrics(self):
        """
        Ground Truth별로 그룹화하여 Consistency 및 Correctness 지표를 계산합니다.

        Returns:
            pd.DataFrame: 각 Ground Truth별 평가 결과 요약 데이터프레임.
        """
        if self.eval_df.empty:
            print("⚠️ 저장된 평가 데이터가 없습니다.")
            return None

        grouped_metrics = []

        # Ground Truth별 그룹화하여 평가 지표 계산
        for ground_truth, group_df in self.eval_df.groupby("ground_truth"):
            results = group_df.iloc[:, 2:-4].values.flatten().tolist()  # inference 결과만 가져오기

            # Confusion Matrix 포함한 지표 계산
            entropy_value, diversity_index, p_value, accuracy, conf_matrix, labels = MetricCalculator.compute_metrics(
                results, ground_truth
            )

            grouped_metrics.append([ground_truth, entropy_value, diversity_index, p_value, accuracy])

            # Confusion Matrix 그리기
            MetricCalculator.plot_confusion_matrix(conf_matrix, labels, ground_truth)

        # 결과를 데이터프레임으로 변환
        summary_df = pd.DataFrame(
            grouped_metrics, columns=["Ground Truth", "Entropy", "Diversity Index", "Chi-Square p-value", "Accuracy"]
        )

        return summary_df

    def print_df(self):
        summary_df = self.group_and_compute_metrics()
        if summary_df is not None:
            print("\n📊 Ground Truth 별 요약된 평가 메트릭")
            print(summary_df)
