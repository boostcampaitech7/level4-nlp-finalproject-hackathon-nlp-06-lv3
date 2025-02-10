from openai import OpenAI

from agents.utils.groundness_check import check_groundness
from agents.utils.utils import build_messages
from utils.configuration import Config
from utils.decorators import retry_with_exponential_backoff
from utils.token_usage_counter import TokenUsageCounter


class SummaryAgent:
    """
    SummaryAgent는 이메일과 같은 텍스트 데이터를 요약하기 위한 에이전트 클래스입니다.
    내부적으로 Upstage 플랫폼의 ChatUpstage 모델을 사용하여 요약 작업을 수행합니다.

    Args:
        model_name (str): 사용할 Upstage AI 모델명입니다(예: 'solar-pro', 'solar-mini').
        summary_type (str): 요약 유형을 지정하는 문자열입니다(예: 'final', 'single' 등).
        temperature (float, optional): 모델 생성에 사용되는 파라미터로, 0에 가까울수록
            결정론적(deterministic) 결과가, 1에 가까울수록 다양성이 높은 결과가 나옵니다.
        seed (int, optional): 모델 결과의 재현성을 높이기 위해 사용하는 난수 시드 값입니다.

    Attributes:
        summary_type (str): 요약 유형을 나타내는 문자열입니다.
    """

    def __init__(self, model_name: str, summary_type: str, temperature=None, seed=None):
        if summary_type != "single" and summary_type != "final":
            raise ValueError(
                f'summary_type: {summary_type}는 허용되지 않는 인자입니다. "single" 혹은 "final"로 설정해주세요.'
            )
        self.model_name = model_name
        self.summary_type = summary_type
        self.temperature = temperature
        self.seed = seed
        self.client = OpenAI(api_key=Config.user_upstage_api_key, base_url="https://api.upstage.ai/v1/solar")

    @retry_with_exponential_backoff()
    def process_with_reflection(self, mail: str, reflections: list = [], max_iteration: int = 3) -> str:
        input_reflections = "제공된 피드백 없음" if reflections else "\n".join(reflections)

        with open("prompt/template/reflexion/single_reflexion_system.txt", "r", encoding="utf-8") as file:
            system_prompt = file.read().strip()
        with open("prompt/template/reflexion/single_reflexion_user.txt", "r", encoding="utf-8") as file:
            user_prompt = file.read().strip()

        user_prompt = user_prompt.format(mail=mail, previous_reflections=input_reflections)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # max_iteration 번 Groundness Check 수행
        return self._generate_with_groundedness(mail, messages, max_iteration)

    def process(self, mail: str, max_iteration: int = 3) -> str:
        messages = build_messages(template_type="summary", target_range=self.summary_type, action="summary", mail=mail)

        return self._generate_with_groundedness(mail, messages, max_iteration)

    @retry_with_exponential_backoff()
    def _generate_with_groundedness(self, mail: str, messages: list[dict], max_iteration: int):
        for i in range(max_iteration):
            response = self.client.chat.completions.create(
                model=self.model_name,
                # ./prompt/template/summary/{self.summary_type}_summary_system(혹은 user).txt 템플릿에서 프롬프트 생성
                messages=messages,
                temperature=self.temperature,
                seed=self.seed,
            )

            TokenUsageCounter.add_usage(
                self.__class__.__name__, f"{self.summary_type}_summary", response.usage.total_tokens
            )

            # Groundness Check
            groundness = check_groundness(
                mail,
                response.choices[0].message.content,
                self.__class__.__name__,
            )

            print(f"{i + 1}번째 사실 확인: {groundness}")
            if groundness == "grounded":
                break

        return response.choices[0].message.content
