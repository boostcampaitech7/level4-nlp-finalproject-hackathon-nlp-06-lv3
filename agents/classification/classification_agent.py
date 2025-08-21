from openai import OpenAI

from agents.utils.utils import build_messages, load_categories_from_yaml
from utils.configuration import Config
from utils.decorators import retry_with_exponential_backoff
from utils.token_usage_counter import TokenUsageCounter


class ClassificationAgent:
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
        self.model_name = model_name
        self.temperature = temperature
        self.seed = seed
        self.client = OpenAI(api_key=Config.user_upstage_api_key, base_url="https://api.upstage.ai/v1/solar")

    @retry_with_exponential_backoff()
    def process(self, summary: str, classification_type: str) -> str:
        """
        주어진 메일(또는 메일 리스트)을 분류하여 해당 레이블 문자열을 반환합니다.

        Args:
            mail (Mail): 분류할 메일 객체(Mail)입니다.

        Returns:
            str: 메일의 분류 결과입니다.
        """

        categories = load_categories_from_yaml(classification_type, is_prompt=True)
        categories_text = ""
        for category in categories:
            categories_text += f"카테고리 명: {category['name']}\n분류 기준: {category['rubric']}\n"

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=build_messages(
                template_type="classification",
                target_range="single",
                action="classification",
                mail=summary,
                categories=categories_text,
            ),
            temperature=self.temperature,
            seed=self.seed,
        )

        TokenUsageCounter.add_usage(self.__class__.__name__, "classification", response.usage.total_tokens)

        label: str = response.choices[0].message.content

        return label
