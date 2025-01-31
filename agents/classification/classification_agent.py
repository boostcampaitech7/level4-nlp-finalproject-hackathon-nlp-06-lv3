import os

from openai import OpenAI

from agents import BaseAgent
from gmail_api import Mail

from ..utils import build_messages, load_categories_from_yaml


class ClassificationAgent(BaseAgent):
    """
    ClassificationAgent는 메일을 분류하는 에이전트 클래스입니다..
    내부적으로 Upstage 플랫폼의 Upstage 모델을 사용하여 요약 작업을 수행합니다.

    Args:
        model_name (str): 사용할 Upstage AI 모델명입니다(예: 'solar-pro', 'solar-mini').
        temperature (float, optional): 모델 생성에 사용되는 파라미터로, 0에 가까울수록
            결정론적(deterministic) 결과가, 1에 가까울수록 다양성이 높은 결과가 나옵니다.
        seed (int, optional): 모델 결과의 재현성을 높이기 위해 사용하는 난수 시드 값입니다.

    Attributes:
        summary_type (str): 요약 유형을 나타내는 문자열입니다.
    """

    def __init__(self, model_name: str, temperature=None, seed=None):
        super().__init__(model=model_name, temperature=temperature, seed=seed)

    def initialize_chat(self, model: str, temperature=None, seed=None):
        """
        요약을 위해 OpenAI 모델 객체를 초기화합니다.

        Args:
            model (str): 사용할 모델 이름.
            temperature (float, optional): 생성 다양성을 조정하는 파라미터.
            seed (int, optional): 결과 재현성을 위한 시드 값.

        Returns:
            OpenAI: 초기화된 Solar 모델 객체.
        """
        return OpenAI(api_key=os.getenv("UPSTAGE_API_KEY"), base_url="https://api.upstage.ai/v1/solar")

    def process(self, mail: Mail) -> str:
        """
        주어진 메일(또는 메일 리스트)을 분류하여 해당 레이블 문자열을 반환합니다.

        Args:
            mail (Mail): 분류할 메일 객체(Mail)입니다.

        Returns:
            str: 메일의 분류 결과입니다.
        """
        if not isinstance(mail, Mail):
            raise ValueError(f"분류 작업에서 {type(mail)} 형식의 데이터가 들어왔습니다.")

        categories = load_categories_from_yaml(is_prompt=True)
        categories_text = ""
        for category in categories:
            categories_text += f"카테고리 명: {category['name']}\n분류 기준: {category['rubric']}\n"

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

        super().add_usage(self.__class__.__name__, "classification", response.usage.total_tokens)

        summarized_content: str = response.choices[0].message.content

        return summarized_content
