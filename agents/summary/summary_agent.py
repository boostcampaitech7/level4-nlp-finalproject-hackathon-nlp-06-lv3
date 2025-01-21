import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_upstage import ChatUpstage

from agents import BaseAgent
from gmail_api import Mail
from prompt import load_template


class SummaryAgent(BaseAgent):
    """
    SummaryAgent는 이메일과 같은 텍스트 데이터를 요약하기 위한 에이전트 클래스입니다.
    내부적으로 Upstage 플랫폼의 ChatUpstage 모델을 사용하여 요약 작업을 수행합니다.

    Args:
        summary_type (str): 요약 유형을 지정하는 문자열입니다(예: 'final', 'single' 등).
        temperature (float, optional): 모델 생성에 사용되는 파라미터로, 0에 가까울수록
            결정론적(deterministic) 결과가, 1에 가까울수록 다양성이 높은 결과가 나옵니다.
        seed (int, optional): 모델 결과의 재현성을 높이기 위해 사용하는 난수 시드 값입니다.

    Attributes:
        summary_type (str): 요약 유형을 나타내는 문자열입니다.
    """

    def __init__(self, summary_type: str, temperature=None, seed=None):
        super().__init__(model="solar-pro", temperature=temperature, seed=seed)
        self.summary_type = summary_type

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

    def process(self, mail: list | Mail, category) -> str:
        """
        주어진 메일(또는 메일 리스트)을 요약하여 문자열 형태로 반환합니다.
        내부적으로는 미리 정의된 템플릿과 결합하여 ChatUpstage 모델에 요약 요청을 보냅니다.

        Args:
            mail (list | Mail): 요약할 메일 객체(Mail) 또는 문자열 리스트입니다.

        Returns:
            str: 요약된 결과 문자열입니다.
        """
        template = load_template("summary", f"{self.summary_type}.txt")
        if isinstance(mail, list):
            concated_mails = "\n".join(f"mail: {mail}, category: {category}")
        else:
            concated_mails = str(mail)

        messages = [
            SystemMessage(content=template),
            HumanMessage(content=concated_mails),
        ]
        response = self.chat.invoke(messages)
        return response.content
