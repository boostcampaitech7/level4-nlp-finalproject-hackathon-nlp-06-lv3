import re

from openai import OpenAI

from utils.configuration import Config
from utils.decorators import retry_with_exponential_backoff
from utils.token_usage_counter import TokenUsageCounter


class ReflexionEvaluator:
    def __init__(self):
        self.model_name = "solar-pro"
        self.client = OpenAI(api_key=Config.user_upstage_api_key, base_url="https://api.upstage.ai/v1/solar")

    @retry_with_exponential_backoff()
    def get_geval_scores(self, source_text: str, output_text: str) -> dict:
        """참조한 텍스트와 생성한 텍스트를 입력으로 받고 점수를 매긴다.

        Args:
            source_text (str): 생성하는 데 참조한 텍스트
            output_text (str): 생성한 텍스트

        Returns:
            g_eval_result (dict): g-eval 결과 딕셔너리
        """
        prompt_path: str = Config.config["report"]["g_eval"]["prompt_path"]

        # 평가할 기준 (기본 4개 + 추가 옵션 포함 시 7개)
        aspects = ["consistency", "coherence", "fluency", "relevance"]

        total_token_usage = 0

        aspect_scores = {}
        for aspect in aspects:
            try:
                with open(f"{prompt_path}{aspect}.txt", "r", encoding="utf-8") as f:
                    base_prompt = f.read()
            except FileNotFoundError as e:
                print(f"[Error] eval_type=report, aspect={aspect}, error={e}")
                aspect_scores[aspect] = 0.0
                continue

            # {Document}, {Summary} 치환
            cur_prompt = base_prompt.format(Document=source_text, Summary=output_text)

            # OpenAI API 호출
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "system", "content": cur_prompt}],
                temperature=0.7,
                max_tokens=50,
                n=1,
            )

            # GPT가 준 output을 float로 변환
            gpt_text = response.choices[0].message.content.strip()

            try:
                # 정규표현식으로 숫자만 추출, 예: "abc123def" -> numbers = ['1','2','3']
                numbers = re.findall(r"\d", gpt_text)
                score_value = float(numbers[-1])
                if score_value > 5:
                    aspect_scores[aspect] = 1.0
                else:
                    aspect_scores[aspect] = score_value
            except Exception as e:
                print(f"[Error] eval_type=report, aspect={aspect}, error={e}")
                aspect_scores[aspect] = 0.0
                continue

            total_token_usage += response.usage.total_tokens

        TokenUsageCounter.add_usage("reflexion", "evaluator", total_token_usage)

        return aspect_scores
