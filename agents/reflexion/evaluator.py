import re

from openai import OpenAI

from utils.configuration import Config
from utils.decorators import retry_with_exponential_backoff
from utils.token_usage_counter import TokenUsageCounter


class ReflexionEvaluator:
    def __init__(self):
        self.model_name = "solar-pro"
        self.client = OpenAI(api_key=Config.user_upstage_api_key, base_url="https://api.upstage.ai/v1/solar")

        self.prompt_path: str = Config.config["report"]["g_eval"]["prompt_path"]
        self.aspects = ["consistency", "coherence", "fluency", "relevance"]

    @retry_with_exponential_backoff()
    def get_geval_scores(self, source_text: str, output_text: str) -> dict:
        """참조한 텍스트와 생성한 텍스트를 입력으로 받고 점수를 매긴다.

        Args:
            source_text (str): 생성하는 데 참조한 텍스트
            output_text (str): 생성한 텍스트

        Returns:
            g_eval_result (dict): g-eval 결과 딕셔너리
        """

        total_token_usage = 0

        aspect_scores = {}
        for aspect in self.aspects:
            cur_prompt = self._create_aspect_prompt(aspect, source_text, output_text)

            # OpenAI API 호출
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "system", "content": cur_prompt}],
                temperature=0.7,
                max_tokens=50,
                n=1,
            )

            try:
                aspect_scores[aspect] = self._extract_score(response.choices[0].message.content.strip())
            except Exception as e:
                print(f"[Error] eval_type=report, aspect={aspect}, error={e}")
                aspect_scores[aspect] = 0.0
                continue

            total_token_usage += response.usage.total_tokens

        TokenUsageCounter.add_usage("reflexion", "evaluator", total_token_usage)

        return aspect_scores

    def _create_aspect_prompt(self, aspect: str, source_text: str, output_text: str) -> str:
        with open(f"{self.prompt_path}{aspect}.txt", "r", encoding="utf-8") as f:
            base_prompt = f.read()

        # {Document}, {Summary} 치환
        return base_prompt.format(Document=source_text, Summary=output_text)

    def _extract_score(self, gpt_text: str):
        # 정규표현식으로 숫자만 추출, 예: "abc123def" -> numbers = ['1','2','3']
        numbers = re.findall(r"\d", gpt_text)
        score_value = float(numbers[-1])
        if score_value > 5:
            return 1.0
        return score_value
