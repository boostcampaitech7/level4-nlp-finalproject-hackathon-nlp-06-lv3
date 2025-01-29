import os

import numpy as np
import pandas as pd
from openai import OpenAI
from scipy.stats import chi2_contingency, entropy
from sklearn.metrics import confusion_matrix

from agents import BaseAgent, ClassificationAgent, build_messages, load_categories_from_yaml
from gmail_api import Mail


class MetricCalculator:
    """Consistency 및 Correctness 평가를 수행하는 클래스."""

    @staticmethod
    def compute_metrics(results: list, ground_truth: list):
        """
        주어진 결과에 대해 Consistency 및 Correctness 평가 수행.

        Args:
            results (list): 분류 모델의 예측 결과 리스트.
            ground_truth (list): 실제 정답 데이터 리스트.

        Returns:
            tuple: (entropy_value, diversity_index, p_value, accuracy)
        """
        value_counts = pd.Series(results).value_counts(normalize=True)
        entropy_value = entropy(value_counts)
        diversity_index = len(value_counts) / len(results)
        chi2, p_value, _, _ = chi2_contingency(pd.crosstab(pd.Series(results), pd.Series(results)))
        conf_matrix = confusion_matrix(ground_truth, results, labels=np.unique(ground_truth + results))
        accuracy = np.trace(conf_matrix) / np.sum(conf_matrix)

        return entropy_value, diversity_index, p_value, accuracy


class EvaluationDataFrameManager:
    """
    평가 데이터 프레임을 관리하는 클래스.
    """

    def __init__(self, inference_count: int):
        self.output_dir = "evaluation/classification/label_data"
        os.makedirs(self.output_dir, exist_ok=True)
        self.csv_file_path = os.path.join(self.output_dir, "labeled.csv")

        self.columns = (
            ["mail_id"]
            + [f"inference_{i+1}" for i in range(inference_count)]
            + ["entropy", "diversity_index", "chi_square_p_value", "accuracy"]
        )

        if os.path.exists(self.csv_file_path):
            self.eval_df = pd.read_csv(self.csv_file_path)
            print(f"📄 기존 평가 데이터 로드 완료: {self.eval_df.shape[0]}개의 데이터")
        else:
            self.eval_df = pd.DataFrame(columns=self.columns)

    def update_eval_df(self, mail_id: str, results: list, ground_truth: list):
        if mail_id in self.eval_df["mail_id"].values:
            print(f"⚠️ 이미 처리된 메일 (ID: {mail_id}), 건너뜁니다.")
            return

        entropy_value, diversity_index, p_value, accuracy = MetricCalculator.compute_metrics(results, ground_truth)
        new_entry = pd.DataFrame(
            [[mail_id] + results + [entropy_value, diversity_index, p_value, accuracy]], columns=self.columns
        )
        self.eval_df = pd.concat([self.eval_df, new_entry], ignore_index=True)
        self.eval_df.to_csv(self.csv_file_path, index=False)

    def print_df(self):
        print(self.eval_df)


class ClassificationEvaluationAgent(BaseAgent):
    """
    GPT 기반 분류 평가를 수행하며 Consistency 및 Correctness를 정량적으로 평가하는 클래스.
    """

    def __init__(self, model: str, human_evaluation: bool, inference: int, temperature: int = None, seed: int = None):
        super().__init__(model, temperature, seed)
        self.inference_iteration = inference
        self.human_evaluation = human_evaluation
        self.df_manager = EvaluationDataFrameManager(inference)

    def initialize_chat(self, model, temperature=None, seed=None):
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_ground_truth(self, mail: Mail) -> str:
        categories = load_categories_from_yaml(is_prompt=True)
        categories_text = "\n".join([f"카테고리 명: {c['name']}\n분류 기준: {c['rubric']}" for c in categories])

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=build_messages(
                template_type="classification",
                target_range="single",
                action="classification",
                mail=str(mail),
                categories=categories_text,
            ),
        )
        return response.choices[0].message.content.strip()

    def process(self, mail: Mail, classifier: ClassificationAgent) -> Mail:
        ground_truth = self.generate_ground_truth(mail)

        if self.human_evaluation:
            user_input = input(
                f"Subject: {mail.subject}\n보낸 사람: {mail.sender}\n본문: {mail.body}\n"
                f"===================\n예측된 정답: {ground_truth}. 수정하려면 입력, 그대로 유지하려면 Enter: "
            )
            ground_truth = user_input.strip() if user_input else ground_truth

        results = [classifier.process(mail) for _ in range(self.inference_iteration)]
        ground_truth_list = [ground_truth] * len(results)
        self.df_manager.update_eval_df(mail.id, results, ground_truth_list)
        return mail

    def print_evaluation(self):
        self.df_manager.print_df()

    @staticmethod
    def calculate_token_cost():
        pass
