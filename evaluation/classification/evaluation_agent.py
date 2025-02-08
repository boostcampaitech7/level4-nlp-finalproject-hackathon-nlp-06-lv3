import os
from collections import Counter

from openai import OpenAI

from agents.classification.classification_agent import ClassificationAgent
from agents.utils.utils import build_messages, load_categories_from_yaml
from evaluation.classification.dataframe_manager import DataFrameManager
from gmail_api.mail import Mail
from utils.utils import retry_with_exponential_backoff


class ClassificationEvaluationAgent:
    """
    AI 모델을 통해 분류(추론)하고, Ground Truth 생성 및 (옵션) 사람 검수 후
    DataFrameManager에 결과를 전달하는 역할.
    """

    def __init__(
        self,
        model_name: str,
        human_evaluation: bool,
        inference_iteration: int,
        temperature: int = None,
        seed: int = None,
    ):
        self.model_name = model_name
        self.human_evaluation = human_evaluation
        self.inference_iteration = inference_iteration
        self.temperature = temperature
        self.seed = seed
        self.df_manager = DataFrameManager(inference_iteration)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_ground_truth(self, summary: str, classification_type: str) -> str:
        """
        1) YAML로부터 카테고리 정보를 로드,
        2) GPT 모델로부터 Ground Truth 추론,
        3) 문자열로 리턴.
        """
        categories = load_categories_from_yaml(classification_type, is_prompt=True)
        categories_text = "\n".join([f"카테고리 명: {c['name']}\n분류 기준: {c['rubric']}" for c in categories])

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=build_messages(
                template_type="classification",
                target_range="single",
                action="classification",
                mail=summary,
                categories=categories_text,
            ),
        )
        return response.choices[0].message.content.strip()

    @retry_with_exponential_backoff()
    def process(self, mail: Mail, summary: str, classifier: ClassificationAgent, classification_type: str):
        """
        1) Ground Truth를 GPT로 생성.
        2) 사람이 검수(human_evaluation) 옵션이 True면 콘솔에서 수정 가능.
        3) 여러 번(inference_iteration) 분류 수행.
        4) 결과를 DataFrameManager에 저장.
        """
        ground_truth = self.generate_ground_truth(summary, classification_type)

        if self.human_evaluation:
            user_input = input(
                "===================\n"
                f"Subject: {mail.subject}\n보낸 사람: {mail.sender}\n본문: {mail.body}\n"
                f"GPT가 제시한 Ground Truth: {ground_truth}\n"
                "이대로 두려면 Enter, 수정하려면 새 값 입력 후 Enter: "
            )
            ground_truth = user_input.strip() if user_input else ground_truth

        results = [classifier.process(summary, classification_type) for _ in range(self.inference_iteration)]

        self.df_manager.update_eval_df(mail.id, results, ground_truth)

        label_counter = Counter(results)
        return label_counter.most_common(1)[0][0]

    def print_evaluation(self):
        """
        최종 평가 결과를 출력(DataFrameManager가 내부적으로 MetricCalculator 호출).
        """
        self.df_manager.print_df()

    @staticmethod
    def calculate_token_cost():
        pass
