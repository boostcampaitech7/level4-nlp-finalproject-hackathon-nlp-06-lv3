from evaluation.gpt_eval import calculate_g_eval
from evaluation.solar_as_judge_eval import run_solar_as_judge
from utils.configuration import Config


class ReflexionEvaluator:
    def __init__(self, task: str):
        self.task = task

    def get_geval_scores(self, source_text: str, output_text: str):
        """참조한 텍스트와 생성한 텍스트를 입력으로 받고 점수를 매긴다.

        Args:
            source_text (str): 생성하는 데 참조한 텍스트
            output_text (str): 생성한 텍스트

        Returns:
            (dict, str)
            0번째는 dict, 1번째는 한 줄의 str 형식으로 aspect 별 점수를 return한다.
        """
        eval_type = "summary" if self.task == "single" else "report"

        return calculate_g_eval(
            source_texts=[source_text],
            generated_texts=[output_text],
            eval_type=eval_type,
        )

    # TODO: 현재 사용되지 않는 함수(개선 및 반영 혹은, 삭제 필요)
    def get_solar_as_judge_result(self, source_text: str, output_text: str):
        """참조한 텍스트와 생성한 텍스트를 입력으로 받고 점수를 매긴다.

        Args:
            source_text (str): 생성하는 데 참조한 텍스트
            output_text (str): 생성한 텍스트

        Returns:
            dict: 생성 텍스트가 각 질문에서 1 또는 0의 결과를 받았는지 return 해준다.
        """
        result = run_solar_as_judge(
            source_texts=source_text,
            generated_texts=output_text,
            solar_as_judge_config=Config.config["evaluation"]["solar_as_judge"],
        )

        return result
