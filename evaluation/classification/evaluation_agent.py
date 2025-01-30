import os

from openai import OpenAI

from agents import BaseAgent, ClassificationAgent, build_messages, load_categories_from_yaml
from gmail_api import Mail

from .dataframe_manager import DataFrameManager


class ClassificationEvaluationAgent(BaseAgent):
    """
    GPT 기반 분류 평가를 수행하며 Consistency 및 Correctness를 정량적으로 평가하는 클래스.

    이 클래스는 OpenAI의 GPT 모델을 활용하여 메일의 분류 결과를 평가하며,
    Consistency(일관성) 및 Correctness(정확도) 등의 지표를 정량적으로 계산합니다.

    Args:
        model (str): 사용할 GPT 계열 모델의 이름.
        human_evaluation (bool): 사람이 직접 평가할 수 있도록 할지 여부.
        inference (int): 동일한 데이터에 대해 추론을 반복하여 일관성을 평가하는 횟수.
        temperature (int, optional): 모델의 응답 다양성을 조절하는 온도 값. 기본값은 None.
        seed (int, optional): 랜덤 시드를 설정하여 결과를 재현 가능하게 함. 기본값은 None.
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
        주어진 메일 데이터를 기반으로 GPT 모델을 사용하여 Ground Truth(정답 데이터)를 생성합니다.

        Args:
            mail (Mail): 분류할 메일 객체.

        Returns:
            str: GPT 모델이 생성한 Ground Truth(정답).
        """
        # YAML 파일에서 카테고리 정보를 로드
        categories = load_categories_from_yaml(is_prompt=True)
        categories_text = "\n".join([f"카테고리 명: {c['name']}\n분류 기준: {c['rubric']}" for c in categories])

        # GPT 모델을 사용하여 분류 수행
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
        """
        메일을 GPT 모델을 사용하여 분류하고, 그 결과를 평가하여 DataFrame에 저장합니다.

        Args:
            mail (Mail): 분류할 메일 객체.
            classifier (ClassificationAgent): 메일을 분류할 ClassificationAgent 객체.

        Returns:
            Mail: 평가가 완료된 메일 객체.
        """
        # Ground Truth(정답) 생성
        ground_truth = self.generate_ground_truth(mail)

        # 사람이 직접 평가하는 옵션이 활성화된 경우, 사용자 입력을 받아 정답 수정 가능
        if self.human_evaluation:
            user_input = input(
                "===================\n"
                f"Subject: {mail.subject}\n보낸 사람: {mail.sender}\n본문: {mail.body}\n"
                f"예측된 정답: {ground_truth}. 수정하려면 입력, 그대로 유지하려면 Enter: "
            )
            ground_truth = user_input.strip() if user_input else ground_truth

        # 동일한 메일에 대해 여러 번 분류하여 일관성 평가
        results = [classifier.process(mail) for _ in range(self.inference_iteration)]

        # 결과 저장
        self.df_manager.update_eval_df(mail.id, results, ground_truth)
        return mail

    def print_evaluation(self):
        self.df_manager.print_df()

    @staticmethod
    def calculate_token_cost():
        pass
