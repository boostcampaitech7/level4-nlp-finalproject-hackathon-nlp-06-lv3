from evaluation.gpt_eval import calculate_g_eval


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
        model_name = "solar-pro"  # TODO: Config로 추출

        return calculate_g_eval(
            source_texts=[source_text],
            generated_texts=[output_text],
            eval_type=eval_type,
            model_name=model_name,
        )
