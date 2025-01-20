from abc import ABC, abstractmethod

from dotenv import load_dotenv


class BaseAgent(ABC):
    """
    BaseAgent는 에이전트 클래스의 기본 인터페이스를 정의하는 추상 클래스입니다.

    모든 에이전트는 이 클래스를 상속받아 특정 작업을 수행하는 메서드를 구현해야 합니다.

    Attributes:
        chat: 외부 API 모델을 사용하는 객체.
    """

    def __init__(self, model: str, temperature=None, seed=None):
        load_dotenv()
        self.chat = self.initialize_chat(model, temperature, seed)

    @abstractmethod
    def initialize_chat(self, model: str, temperature=None, seed=None):
        """
        특정 모델을 초기화합니다.

        Args:
            model (str): 사용할 모델 이름.
            temperature (float, optional): 생성 다양성을 조정하는 파라미터.
            seed (int, optional): 결과 재현성을 위한 시드 값.
        """
        pass

    @abstractmethod
    def process(self, data):
        """
        데이터를 처리하는 메서드입니다. 하위 클래스에서 구현해야 합니다.

        Args:
            data: 처리할 데이터.

        Returns:
            처리 결과.
        """
        pass
