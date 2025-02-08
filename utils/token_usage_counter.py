from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np


class TokenUsageCounter:
    token_usage_records = []

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

        for record in TokenUsageCounter.token_usage_records:
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

    @staticmethod
    def get_total_token_cost():
        return sum(record["tokens"] for record in TokenUsageCounter.token_usage_records)
