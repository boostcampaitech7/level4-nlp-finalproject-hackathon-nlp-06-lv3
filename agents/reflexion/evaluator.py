from agents.base_agent import BaseAgent
from evaluation import calculate_g_eval, run_solar_as_judge
from utils.utils import retry_with_exponential_backoff


class ReflexionEvaluator(BaseAgent):
    def __init__(self, task: str, config: dict):
        self.config = config
        self.task = task

    def initialize_chat(self, model, temperature=None, seed=None):
        pass

    def process(self, data, model=None):
        pass

    @retry_with_exponential_backoff()
    def get_geval_scores(self, source_text: str, output_text: str):
        """참조한 텍스트와 생성한 텍스트를 입력으로 받고 점수를 매긴다.

        Args:
            source_text (str): 생성하는 데 참조한 텍스트
            output_text (str): 생성한 텍스트

        Returns:
            (dict, str)
            0번째는 dict, 1번째는 한 줄의 str 형식으로 aspect 별 점수를 return한다.
        """
        eval_list, token_usage = calculate_g_eval(
            source_texts=[source_text],
            generated_texts=[output_text],
            g_eval_config=self.config["summary"]["g_eval"],
            eval_type=self.task,
        )

        super().add_usage("reflexion", "evaluator", token_usage)

        return eval_list, token_usage

    @retry_with_exponential_backoff()
    def get_solar_as_judge_result(self, source_text: str, output_text: str):
        """참조한 텍스트와 생성한 텍스트를 입력으로 받고 점수를 매긴다.

        Args:
            source_text (str): 생성하는 데 참조한 텍스트
            output_text (str): 생성한 텍스트

        Returns:
            dict: 생성 텍스트가 각 질문에서 1 또는 0의 결과를 받았는지 return 해준다

        super().add_usage("reflexion", "evaluator", token_usage)

        """

        result = run_solar_as_judge(
            source_texts=source_text,
            generated_texts=output_text,
            solar_as_judge_config=self.config["evaluation"]["solar_as_judge"],
        )

        return result
