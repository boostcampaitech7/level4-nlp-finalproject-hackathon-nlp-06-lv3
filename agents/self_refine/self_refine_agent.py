import json

from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

from agents.self_refine.json_formats import FEEDBACK_FORMAT
from agents.utils.groundness_check import check_groundness
from gmail_api.mail import Mail
from utils.configuration import Config
from utils.decorators import retry_with_exponential_backoff
from utils.token_usage_counter import TokenUsageCounter


class SelfRefineAgent:
    """
    SelfRefineAgent는 이메일 요약 및 데일리 레포트를 생성하는 기능을 제공하는 에이전트 클래스입니다.
    내부적으로 Self-Refine 프로세스를 사용하여 결과를 반복적으로 개선합니다.

    Args:
        model_name (str): 사용할 Upstage AI 모델명입니다(예: 'solar-pro', 'solar-mini').
        target_range (str): Self-refine을 적용할 범위(예: 'single', 'final')
        temperature (float, optional): 모델 생성 다양성을 조정하는 파라미터.
        seed (int, optional): 결과 재현성을 위한 시드 값.
    """

    def __init__(self, model_name: str, temperature=None, seed=None):
        self.model_name = model_name
        self.temperature = temperature
        self.seed = seed
        self.client = OpenAI(api_key=Config.user_upstage_api_key, base_url="https://api.upstage.ai/v1/solar")

    @retry_with_exponential_backoff()
    def feedback(self, mail: Mail, summary: str) -> ChatCompletion:
        with open("prompt/template/self_refine/feedback_system.txt", "r", encoding="utf-8") as file:
            system_prompt = file.read().strip()
        with open("prompt/template/self_refine/feedback_user.txt", "r", encoding="utf-8") as file:
            user_prompt = file.read().strip().format(mail=str(mail), summary=summary)
        return self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=FEEDBACK_FORMAT,
            temperature=self.temperature,
            seed=self.seed,
        )

    @retry_with_exponential_backoff()
    def refine(self, mail: Mail, summary: str, feedback: str) -> ChatCompletion:
        with open("prompt/template/self_refine/refine_system.txt", "r", encoding="utf-8") as file:
            system_prompt = file.read().strip()
        with open("prompt/template/self_refine/refine_user.txt", "r", encoding="utf-8") as file:
            user_prompt = file.read().strip().format(mail=str(mail), summary=summary, feedback=feedback)

        return self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.temperature,
            seed=self.seed,
        )

    @retry_with_exponential_backoff()
    def process(self, mail: Mail, summary: str, max_iteration: int = 3):
        """
        Self-refine 하여 최종 결과물을 반환합니다.

        Args:
            data (Mail | dict[str, Mail]): 입력 데이터.
            model (BaseAgent): 데이터를 처리하는 모델(ex. SummaryAgent).
            max_iteration (int): 최대 Self-refine 반복 횟수.

        Return:
            str: Self-refine을 거친 최종 결과물.
        """
        print("Self-refine 중...")
        for i in range(max_iteration):
            groundness = check_groundness(
                str(mail),
                summary,
                self.__class__.__name__,
            )
            print(f"Self-refine {i + 1} 회차")

            feedback_response: ChatCompletion = self.feedback(mail, summary)
            TokenUsageCounter.add_usage(self.__class__.__name__, "feedback", feedback_response.usage.total_tokens)

            feedback = json.loads(feedback_response.choices[0].message.content)

            if feedback["evaluation"] == "STOP" and len(feedback["issues"]) == 0 and groundness == "grounded":
                print(f"Self-refine {i + 1} 회차에서 종료")
                break

            revision_response: ChatCompletion = self.refine(mail, summary, feedback["issues"])
            summary = revision_response.choices[0].message.content
            TokenUsageCounter.add_usage(self.__class__.__name__, "refine", revision_response.usage.total_tokens)

        return summary
