import json
import os

from openai import OpenAI

from agents.base_agent import BaseAgent
from agents.groundness_check import check_groundness
from agents.utils import FEEDBACK_FORMAT, build_messages, generate_plain_text_report
from utils.token_usage_counter import TokenUsageCounter
from utils.utils import retry_with_exponential_backoff


class SelfRefineAgent(BaseAgent):
    """
    SelfRefineAgent는 이메일 요약 및 데일리 레포트를 생성하는 기능을 제공하는 에이전트 클래스입니다.
    내부적으로 Self-Refine 프로세스를 사용하여 결과를 반복적으로 개선합니다.

    Args:
        model_name (str): 사용할 Upstage AI 모델명입니다(예: 'solar-pro', 'solar-mini').
        target_range (str): Self-refine을 적용할 범위(예: 'single', 'final')
        temperature (float, optional): 모델 생성 다양성을 조정하는 파라미터.
        seed (int, optional): 결과 재현성을 위한 시드 값.
    """

    def __init__(self, model_name: str, target_range: str, api_key: str, temperature=None, seed=None):
        self.api_key = api_key
        super().__init__(model_name, temperature, seed)
        if target_range != "single" and target_range != "final":
            raise ValueError(
                f'target_range: {target_range}는 허용되지 않는 인자입니다. "single" 혹은 "final"로 설정해주세요.'
            )
        self.target_range = target_range
        self.temperature = temperature
        self.seed = seed

    def initialize_chat(self):
        """
        ChatUpstage 모델을 초기화합니다.

        Returns:
            ChatUpstage: 초기화된 ChatUpstage 객체.
        """
        return OpenAI(api_key=self.api_key, base_url="https://api.upstage.ai/v1/solar")

    def logging(self, path, content):
        diretory = os.path.dirname(path)
        os.makedirs(diretory, exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"{path} 로그 파일이 생성되었습니다.")

    @retry_with_exponential_backoff()
    def feedback(self, feedback_messages: str):
        return self.client.chat.completions.create(
            model=self.model_name,
            messages=feedback_messages,
            response_format=FEEDBACK_FORMAT,
            temperature=self.temperature,
            seed=self.seed,
        )

    @retry_with_exponential_backoff()
    def refine(self, refine_messages: str):
        return self.client.chat.completions.create(
            model=self.model_name,
            messages=refine_messages,
            response_format=None,
            temperature=self.temperature,
            seed=self.seed,
        )

    @retry_with_exponential_backoff()
    def process(self, data, model: BaseAgent, max_iteration: int = 3):
        """
        Self-refine 하여 최종 결과물을 반환합니다.

        Args:
            data (Mail | dict[str, Mail]): 입력 데이터.
            model (BaseAgent): 데이터를 처리하는 모델(ex. SummaryAgent).
            max_iteration (int): 최대 Self-refine 반복 횟수.

        Return:
            str: Self-refine을 거친 최종 결과물.
        """
        # 초기 요약 및 로그 생성
        summarization = model.process(str(data))
        refine_target: dict = summarization["summary"] if self.target_range == "single" else summarization
        logging_file_prefix = self.target_range
        logging_file_prefix += "_".join(data.id.split("/")) if self.target_range == "single" else ""
        self.logging(
            f"./agents/self_refine/log/{logging_file_prefix}_init.txt", generate_plain_text_report(refine_target)
        )

        # 데이터 문자열로 전처리
        if self.target_range == "single":
            input_mail_data = str(data)
        else:
            input_mail_data = "\n".join(
                [f"메일 id: {item.id} 분류: {item.label_category} 요약: {item.summary}" for _, item in data.items()]
            )

        # Self Refine 반복
        for i in range(max_iteration):
            # Groundness Check
            groundness = check_groundness(
                input_mail_data, generate_plain_text_report(refine_target), self.api_key, self.__class__.__name__
            )

            # Feedback
            feedback_messages = build_messages(
                template_type="self_refine",
                target_range=self.target_range,
                action="feedback",
                mails=input_mail_data,
                report=refine_target,
            )
            feedback_response = self.feedback(feedback_messages)
            feedback = feedback_response.choices[0].message.content
            TokenUsageCounter.add_usage(self.__class__.__name__, "feedback", feedback_response.usage.total_tokens)

            self.logging(
                f"./agents/self_refine/log/{logging_file_prefix}_self_refine_{i}_feedback.txt",
                f"feedback: {feedback}\n groundness: {groundness}",
            )
            feedback_dict = json.loads(feedback)

            # 조기 종료 조건
            if feedback_dict["evaluation"] == "STOP" and len(feedback_dict["issues"]) == 0 and groundness == "grounded":
                break

            # Refine
            refine_messages = build_messages(
                template_type="self_refine",
                target_range=self.target_range,
                action="refine",
                mails=input_mail_data,
                report=refine_target,
                reasoning=str(feedback_dict["issues"]),  # TODO: 메일 요약문과 피드백을 하나로 처리할 것
            )
            revision_response = self.refine(refine_messages)
            revision_content = revision_response.choices[0].message.content
            TokenUsageCounter.add_usage(self.__class__.__name__, "refine", revision_response.usage.total_tokens)

            # 요약문 혹은 리포트 업데이트 및 로깅
            refine_target = json.loads(revision_content) if self.target_range == "final" else revision_content
            self.logging(f"./agents/self_refine/log/{logging_file_prefix}_self_refine_{i}_refine.txt", revision_content)

        return refine_target
