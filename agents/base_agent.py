# Note
# BaseAgent 클래스는 파이프라인 내 모델을 객체 지향적으로 관리하고자 생성된 클래스입니다.
# 향후 **모델이 공통으로 처리하는 동작(e.g. Groundness Check)**이 있는 경우,
# 추가 @abstractmethod를 선언해서 Agent 클래스를 전체 관리해주세요.

from abc import ABC, abstractmethod
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
from openai import OpenAI


class BaseAgent(ABC):
    """
    BaseAgent는 에이전트 클래스의 기본 인터페이스를 정의하는 추상 클래스입니다.

    모든 에이전트는 이 클래스를 상속받아 특정 작업을 수행하는 메서드를 구현해야 합니다.

    Attributes:
        chat: 외부 API 모델을 사용하는 객체.
    """

    token_usage_records = []

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

    @classmethod
    def add_usage(cls, agent_name: str, usage_type: str, tokens: int):
        """
        에이전트명, 액션(혹은 작업) 종류, 사용된 토큰 수를 기록합니다.
        """
        cls.token_usage_records.append({"agent_name": agent_name, "usage_type": usage_type, "tokens": tokens})

    @staticmethod
    def plot_token_cost():
        """
        기록된 토큰 사용량(token_usage_records)을 토대로 Grouped Bar Chart를 그립니다.
        - X축: usage_type (예: 'classification', 'single_summary', 'feedback', ...)
        - 각 usage_type 그룹 안에서 에이전트별 막대를 나란히 배치
        """
        # (agent_name, usage_type) 별 토큰 사용량을 합산
        usage_dict = defaultdict(int)
        agents_set = set()
        usage_types_set = set()

        for record in BaseAgent.token_usage_records:
            agent_name = record["agent_name"]
            usage_type = record["usage_type"]
            tokens = record["tokens"]

            usage_dict[(agent_name, usage_type)] += tokens
            agents_set.add(agent_name)
            usage_types_set.add(usage_type)

        # 정렬된 리스트(그래프에서 일정 순서를 유지하기 위해)
        agents_list = sorted(list(agents_set))
        usage_types_list = sorted(list(usage_types_set))

        # X축 인덱스 설정
        x = np.arange(len(usage_types_list))  # usage_type 별 index
        # 에이전트가 여러 개라면, 한 usage_type 그룹 안에서 막대를 나란히 배치하기 위한 폭
        bar_width = 0.8 / len(agents_list)

        plt.figure(figsize=(10, 6))

        # 에이전트 별로 막대(Bar) 생성
        for i, agent in enumerate(agents_list):
            y_values = []
            for usage_type in usage_types_list:
                y_values.append(usage_dict.get((agent, usage_type), 0))

            # 막대를 오른쪽으로 조금씩 이동
            plt.bar(x + i * bar_width, y_values, bar_width, label=agent)

        # X축 레이블을 usage_type의 중앙에 놓기
        plt.xticks(x + (bar_width * (len(agents_list) - 1) / 2), usage_types_list, rotation=30, ha="right")

        plt.xlabel("Usage Type")
        plt.ylabel("Token Usage")
        plt.title("Token Usage by Agent and Call Type")
        plt.legend(title="Agents", loc="best")
        plt.tight_layout()
        plt.savefig("token-usage.png")
