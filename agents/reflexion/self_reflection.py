from openai import OpenAI

from utils.configuration import Config
from utils.decorators import retry_with_exponential_backoff
from utils.token_usage_counter import TokenUsageCounter


class ReflexionSelfReflection:
    def __init__(self):
        self.model_name = "solar-pro"
        self.temperature = 0.7
        self.seed = 42
        self.reflection_memory: list[str] = []
        self.client = OpenAI(api_key=Config.user_upstage_api_key, base_url="https://api.upstage.ai/v1/solar")
        # Reflexion 프롬프트 템플릿을 읽어온다
        with open("prompt/template/reflexion/reflexion_final.txt", "r", encoding="utf-8") as file:
            self.reflection_template = file.read()
        # aspect 별 채점 기준을 읽어온다
        with open("prompt/template/reflexion/g_eval/aspects_description_final.txt", "r", encoding="utf-8") as file:
            self.aspects_description = file.read()

    @retry_with_exponential_backoff()
    def generate_reflection(self, source_text, output_text, eval_result):
        """
        참조된 텍스트와 생성 텍스트를 입력으로 받고 Reflection을 생성한다.

        Args:
            source_input (str): 생성할 때 참조된 텍스트
            summary_output (str): 생성된  텍스트
            eval_result (str): 평가 점수
        """
        formatted_prompt = self.reflection_template.format(
            source_input=source_text,
            source_output=output_text,
            eval_result=eval_result,
            eval_aspects_description=self.aspects_description,
            previous_reflections=self.get_reflection_memory_str(),
        )

        # 메시지 구성
        messages = [
            {"role": "system", "content": formatted_prompt},
            {"role": "user", "content": self.aspects_description},
        ]

        # 모델에게 메시지를 전달해 리플렉션 결과 받기
        reflection_response = self.client.chat.completions.create(
            model=self.model_name, messages=messages, temperature=self.temperature, seed=self.seed
        )
        reflection_text = reflection_response.choices[0].message.content

        # 리플렉션 결과를 메모리에 추가
        self.save_reflection(reflection_text)

        TokenUsageCounter.add_usage("reflexion", "self-reflection", reflection_response.usage.total_tokens)

    def get_reflection_memory_str(self):
        if not self.reflection_memory:
            return "없음"
        return "\n".join(self.reflection_memory)

    def save_reflection(self, reflection_text: str):
        """reflection 메모리에 reflection을 저장한다.

        Args:
            reflection_text (str)
        """
        self.reflection_memory.append(reflection_text)
