import os

from langchain_upstage import ChatUpstage

from agents import BaseAgent
from gmail_api import Mail
from prompt import load_template_with_variables


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
        self.target_range = target_range

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
        return ChatUpstage(api_key=os.getenv("UPSTAGE_API_KEY"), model=model, temperature=temperature, seed=seed)

    def process(self, data: Mail | list, model: BaseAgent, max_iteration: int = 3):
        """
        Self-refine 하여 최종 결과물을 반환합니다.

        Args:
            data (Mail | list): 입력 데이터.
            model (BaseAgent): 데이터를 처리하는 모델(ex. SummaryAgent).
            max_iteration (int): 최대 Self-refine 반복 횟수.

        Return:
            str: Self-refine을 거친 최종 결과물.
        """
        # 초기 요약
        report = model.process(data)

        if isinstance(data, list):
            concated_mails = "\n".join(data)

        for i in range(max_iteration):
            feedback_reponse = self.chat.invoke(
                load_template_with_variables(
                    template_type="self_refine",
                    file_name=f"{self.target_range}_feedback.txt",
                    mails=concated_mails,
                    report=report,
                )
            )
            feedback = feedback_reponse.content
            if "STOP" in feedback:
                break

            report_response = self.chat.invoke(
                load_template_with_variables(
                    template_type="self_refine",
                    file_name=f"{self.target_range}_refine.txt",
                    mails=concated_mails,
                    report=report,
                    reasoning=feedback,
                )
            )
            report = report_response.content
            print(f"---{i}번째-self-refine---")
            print(f"feedback: {feedback}")
            print(f"refine 후: {report}")

        return report
