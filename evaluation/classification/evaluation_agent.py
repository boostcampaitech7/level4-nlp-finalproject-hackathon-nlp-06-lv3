import os
from collections import Counter

from openai import OpenAI

from agents import BaseAgent, ClassificationAgent, build_messages, load_categories_from_yaml
from gmail_api import Mail

from .dataframe_manager import DataFrameManager


class ClassificationEvaluationAgent(BaseAgent):
    """
    AI 모델을 통해 분류(추론)하고, Ground Truth 생성 및 (옵션) 사람 검수 후
    DataFrameManager에 결과를 전달하는 역할.
    """

    def __init__(self, model: str, human_evaluation: bool, inference: int, temperature: int = None, seed: int = None):
        super().__init__(model, temperature, seed)
        self.inference_iteration = inference
        self.human_evaluation = human_evaluation
        self.df_manager = DataFrameManager(inference)

    def initialize_chat(self, model, temperature=None, seed=None):
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_ground_truth(self, mail: Mail) -> str:
        """
        1) YAML로부터 카테고리 정보를 로드,
        2) GPT 모델로부터 Ground Truth 추론,
        3) 문자열로 리턴.
        """
        categories = load_categories_from_yaml(is_prompt=True)
        categories_text = "\n".join([f"카테고리 명: {c['name']}\n분류 기준: {c['rubric']}" for c in categories])

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=build_messages(
                template_type="classification",
                target_range="single",
                action="classification",
                mail=mail.summary,
                categories=categories_text,
            ),
        )
        return response.choices[0].message.content.strip()

    def process(self, mail: Mail, classifier: ClassificationAgent) -> str:
        """
        1) Ground Truth를 GPT로 생성.
        2) 사람이 검수(human_evaluation) 옵션이 True면 콘솔에서 수정 가능.
        3) 여러 번(inference_iteration) 분류 수행.
        4) 결과를 DataFrameManager에 저장.
        """
        ground_truth = self.generate_ground_truth(mail)

        if self.human_evaluation:
            user_input = input(
                "===================\n"
                f"Subject: {mail.subject}\n보낸 사람: {mail.sender}\n본문: {mail.body}\n"
                f"GPT가 제시한 Ground Truth: {ground_truth}\n"
                "이대로 두려면 Enter, 수정하려면 새 값 입력 후 Enter: "
            )
            ground_truth = user_input.strip() if user_input else ground_truth

        # 동일 메일에 대해 여러 번 분류
        results = [classifier.process(mail) for _ in range(self.inference_iteration)]

        # CSV에 저장 (메일 단위로 Entropy 등 기록)
        self.df_manager.update_eval_df(mail.id, results, ground_truth)

        # 여기서는 majority vote 등으로 최종값 return (예: 가장 많이 나온 라벨)
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
