# Note
# BaseAgent 클래스는 파이프라인 내 모델을 객체 지향적으로 관리하고자 생성된 클래스입니다.
# 향후 **모델이 공통으로 처리하는 동작(e.g. Groundness Check)**이 있는 경우,
# 추가 @abstractmethod를 선언해서 Agent 클래스를 전체 관리해주세요.

from abc import ABC, abstractmethod

from openai import OpenAI


class BaseAgent(ABC):
    """
    BaseAgent는 에이전트 클래스의 기본 인터페이스를 정의하는 추상 클래스입니다.

    모든 에이전트는 이 클래스를 상속받아 특정 작업을 수행하는 메서드를 구현해야 합니다.

    Attributes:
        chat: 외부 API 모델을 사용하는 객체.
    """

    def __init__(self, model: str, temperature=None, seed=None):
        # response_format을 사용하기 위해 OpenAI 객체로 선언합니다.
        # response_format과 JsonOutputParser의 차이는 다음 링크에서 간단하게 설명합니다.
        # https://www.notion.so/gamchan/OpenAI-182815b39d398070b7fbc783bd7205ca?pvs=4
        self.client: OpenAI = self.initialize_chat(model, temperature, seed)
        self.model_name = model
        self.temperature = temperature
        self.seed = seed
        self.token_monitor = None

    @abstractmethod
    def initialize_chat(self, model: str, temperature=None, seed=None) -> OpenAI:
        """
        특정 모델을 초기화합니다.

        Args:
            model (str): 사용할 모델 이름.
            temperature (float, optional): 생성 다양성을 조정하는 파라미터.
            seed (int, optional): 결과 재현성을 위한 시드 값.
        """
        pass

    @abstractmethod
    def process(self, data, model=None):
        """
        데이터를 처리하는 메서드입니다. 하위 클래스에서 구현해야 합니다.

        Args:
            data: 처리할 데이터.
            model: 데이터를 처리하는 모델.

        Returns:
            처리 결과.
        """
        pass

    @staticmethod
    @abstractmethod
    def calculate_token_cost():
        pass
