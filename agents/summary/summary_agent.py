import json
import os

from openai import OpenAI

from agents import BaseAgent, check_groundness
from gmail_api import Mail

from ..utils import REPORT_FORMAT, SUMMARY_FORMAT, build_messages, generate_plain_text_report


class SummaryAgent(BaseAgent):
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
        super().__init__(model=model_name, temperature=temperature, seed=seed)

        # SummaryAgent 객체 선언 시 summary_type을 single|final로 강제합니다.
        if summary_type != "single" and summary_type != "final":
            raise ValueError(
                f'summary_type: {summary_type}는 허용되지 않는 인자입니다. "single" 혹은 "final"로 설정해주세요.'
            )

        # 추후 프롬프트 템플릿 로드 동작을 위해 string으로 받아 attribute로 저장합니다.
        self.summary_type = summary_type
        self.temperature = temperature
        self.seed = seed

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

    def process(self, mail: dict[Mail] | Mail, max_iteration: int = 3) -> dict:
        """
        주어진 메일(또는 메일 리스트)을 요약하여 JSON 형태로 반환합니다.
        내부적으로는 미리 정의된 템플릿과 결합하여 Solar 모델에 요약 요청을 보냅니다.

        Args:
            mail (dict[Mail] | Mail): 요약할 메일 객체(Mail) 또는 문자열 리스트.
            max_iteration (int): 최대 Groundness Check 횟수.

        Returns:
            dict: 요약된 결과 JSON.
            token_usage (int): process 함수 실행 중 발생한 토큰 이용량.
        """
        # self.summary_type에 따라 데이터 유효 검증 로직
        if (self.summary_type == "single" and not isinstance(mail, Mail)) or (
            self.summary_type == "final" and not isinstance(mail, dict)
        ):
            raise ValueError(f"{self.summary_type}의 잘못된 타입의 데이터 {type(mail)}가 들어왔습니다.")

        # 출력 포맷 지정
        response_format = SUMMARY_FORMAT if self.summary_type == "single" else REPORT_FORMAT

        # LLM 입력을 위한 문자열 처리
        input_mail_data = ""
        if self.summary_type == "single":
            input_mail_data = str(mail)
        else:
            input_mail_data = "\n".join(
                [f"메일 id: {item.id} 분류: {item.label} 요약문: {item.summary}" for _, item in mail.items()]
            )

        token_usage = 0
        # max_iteration 번 Groundness Check 수행
        for i in range(max_iteration):
            response = self.client.chat.completions.create(
                model=self.model_name,
                # ./prompt/template/summary/{self.summary_type}_summary_system(혹은 user).txt 템플릿에서 프롬프트 생성
                messages=build_messages(
                    template_type="summary", target_range=self.summary_type, action="summary", mail=input_mail_data
                ),
                response_format=response_format,
                temperature=self.temperature,
                seed=self.seed,
            )
            summarized_content: dict = json.loads(response.choices[0].message.content)

            super().add_usage(self.__class__.__name__, f"{self.summary_type}_summary", response.usage.total_tokens)
            token_usage += response.usage.total_tokens

            # Groundness Check를 위해 JSON 결과에서 문자열 정보 추출
            if self.summary_type == "single":
                result = summarized_content["summary"]
            else:
                result = generate_plain_text_report(summarized_content)

            # Groundness Check
            groundness, groundness_token_usage = check_groundness(context=input_mail_data, answer=result)
            super().add_usage(self.__class__.__name__, f"{self.summary_type}_groundness_check", groundness_token_usage)
            token_usage += groundness_token_usage

            print(f"{i + 1}번째 사실 확인: {groundness}")
            if groundness == "grounded":
                break

        return summarized_content, token_usage
