import json
import os

from openai import OpenAI

from agents import BaseAgent, check_groundness
from gmail_api import Mail

from ..utils import REPORT_FEEDBACK_FORMAT, REPORT_REFINE_FORMAT, create_message_arg


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

    def __init__(self, model_name: str, target_range: str, temperature=None, seed=None):
        super().__init__(model=model_name, temperature=temperature, seed=seed)
        if target_range != "single" and target_range != "final":
            raise KeyError(
                f'target_range: {target_range}는 허용되지 않는 인자입니다. "single" 혹은 "final"로 설정해주세요.'
            )
        self.model_name = model_name
        self.target_range = target_range
        self.temperature = temperature

    def initialize_chat(self, model: str, temperature=None, seed=None):
        """
        ChatUpstage 모델을 초기화합니다.

        Args:
            model (str): 사용할 모델 이름.
            temperature (float, optional): 생성 다양성을 조정하는 파라미터.
            seed (int, optional): 결과 재현성을 위한 시드 값.

        Returns:
            ChatUpstage: 초기화된 ChatUpstage 객체.
        """
        return OpenAI(api_key=os.getenv("UPSTAGE_API_KEY"), base_url="https://api.upstage.ai/v1/solar")

    def logging(self, path, content):
        diretory = os.path.dirname(path)
        os.makedirs(diretory, exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"{path} 로그 파일이 생성되었습니다.")

    def process(self, data: Mail | dict[str, Mail], model: BaseAgent, max_iteration: int = 3):
        """
        Self-refine 하여 최종 결과물을 반환합니다.

        Args:
            data (Mail | dict[str, Mail]): 입력 데이터.
            model (BaseAgent): 데이터를 처리하는 모델(ex. SummaryAgent).
            max_iteration (int): 최대 Self-refine 반복 횟수.

        Return:
            str: Self-refine을 거친 최종 결과물.
        """
        if isinstance(data, dict):
            concated_mails = "\n".join([f"분류: {item.label} 요약: {item.summary}" for _, item in data.items()])
        else:
            concated_mails = str(data)
        # 초기 요약
        report = model.process(data)
        self.logging("./agents/self_refine/log/init_report.txt", report)

        for i in range(max_iteration):
            groundness = check_groundness(context=concated_mails, answer=report)

            feedback_reponse = self.client.chat.completions.create(
                model=self.model_name,
                messages=create_message_arg(
                    template_type="self_refine",
                    target_range="final",
                    action="feedback",
                    mails=concated_mails,
                    report=report,
                ),
                response_format=REPORT_FEEDBACK_FORMAT,
            )
            feedback = feedback_reponse.choices[0].message.content
            self.logging(
                f"./agents/self_refine/log/self_refine_{i}_feedback.txt",
                f"feedback: {feedback}\n groundness: {groundness}",
            )
            feedback_dict = json.loads(feedback)

            if feedback_dict["evaluation"] == "STOP" and groundness == "grounded":
                break

            report_response = self.client.chat.completions.create(
                model=self.model_name,
                messages=create_message_arg(
                    template_type="self_refine",
                    target_range="final",
                    action="refine",
                    mails=concated_mails,
                    report=report,
                    reasoning=str(feedback_dict["issues"]),  # TODO: 메일 요약문과 피드백을 하나로 처리할 것
                ),
                response_format=REPORT_REFINE_FORMAT,
            )
            report_content = report_response.choices[0].message.content
            report_dict = json.loads(report_content)
            report = report_dict["final_report"]
            self.logging(f"./agents/self_refine/log/self_refine_{i}_refine.txt", report)

        return report

    @staticmethod
    def calculate_token_cost():
        pass
