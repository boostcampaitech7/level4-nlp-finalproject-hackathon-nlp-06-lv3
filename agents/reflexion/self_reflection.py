import os

from openai import OpenAI

from agents.base_agent import BaseAgent
from utils import retry_with_exponential_backoff
from utils.token_usage_counter import TokenUsageCounter


class ReflexionSelfReflection(BaseAgent):
    def __init__(self, task):
        super().__init__("solar-pro", 0.7, 42)
        # Reflection을 담을 리스트를 선언해준다
        self.reflection_memory = []
        self.reflection_template = None
        self.aspects_description = None
        self.task = task

    def initialize_chat(self):
        """
        요약을 위해 OpenAI 모델 객체를 초기화합니다.

        Returns:
            OpenAI: 초기화된 Solar 모델 객체.
        """
        return OpenAI(
            api_key=os.getenv("UPSTAGE_API_KEY"), base_url="https://api.upstage.ai/v1/solar"
        )  # TODO: UPSTAGE_API_KEY user 별로 사용하게 변경

    def process(self, data, model=None):
        pass

    def load_setup_texts(self):
        # Reflexion 프롬프트 템플릿을 읽어온다
        reflexion_template_name = f"reflexion_{self.task}.txt"
        reflexion_template_directory = f"prompt/template/reflexion/{reflexion_template_name}"
        with open(reflexion_template_directory, "r", encoding="utf-8") as file:
            self.reflection_template = file.read()

        # aspect 별 채점 기준을 읽어온다
        aspects_description_name = f"aspects_description_{self.task}.txt"
        reflexion_template_directory = f"prompt/template/g_eval/{aspects_description_name}"
        with open(reflexion_template_directory, "r", encoding="utf-8") as file:
            self.aspects_description = file.read()

    def save_reflection(self, reflection_text):
        """reflection 메모리에 reflection을 저장한다.

        Args:
            reflection_text (str)
        """
        self.reflection_memory.append(reflection_text)

    @retry_with_exponential_backoff()
    def generate_reflection(self, source_text, output_text, eval_result):
        """
        참조된 텍스트와 생성 텍스트를 입력으로 받고 Reflection을 생성한다.

        Args:
            source_input (str): 생성할 때 참조된 텍스트
            summary_output (str): 생성된  텍스트
            eval_result (str): 평가 점수

        Returns:
            str: generated reflection
        """
        if not self.reflection_memory:
            previous_reflections = "없음"
        else:
            previous_reflections = "\n".join(self.reflection_memory)

        formatted_prompt = self.reflection_template.format(
            source_input=source_text,
            source_output=output_text,
            eval_result=eval_result,
            eval_aspects_description=self.aspects_description,
            previous_reflections=previous_reflections,
        )

        # 메시지 구성
        messages = [{"role": "user", "content": formatted_prompt}]

        # 모델에게 메시지를 전달해 리플렉션 결과 받기
        reflection_response = self.client.chat.completions.create(
            model=self.model_name, messages=messages, temperature=self.temperature, seed=self.seed
        )
        reflection_text = reflection_response.choices[0].message.content

        # 리플렉션 결과를 메모리에 추가
        self.save_reflection(reflection_text)

        TokenUsageCounter.add_usage("reflexion", "self-reflection", reflection_response.usage.total_tokens)
