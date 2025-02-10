from agents.reflexion.evaluator import ReflexionEvaluator
from agents.reflexion.self_reflection import ReflexionSelfReflection
from agents.summary.summary_agent import SummaryAgent
from utils.configuration import Config


class ReflexionFramework:
    def __init__(self):
        self.summary_agent = SummaryAgent(
            model_name="solar-pro",
            summary_type="final",
            temperature=Config.config["temperature"]["summary"],
            seed=Config.config["seed"],
        )
        self.evaluator = ReflexionEvaluator()
        self.self_reflection = ReflexionSelfReflection()
        self.threshold = Config.config["reflexion"]["threshold"]
        self.max_iteration = Config.config["reflexion"]["max_iteration"]

    def process(self, origin_mail) -> str:
        """
        Reflexion을 실행합니다.

        Args:

        Returns:
            모든 aspect 점수의 평균값이 제일 높은 text가 반환됩니다.
        """
        outputs = []
        eval_results = []
        final_output = ""
        max_score = 0

        for i in range(self.max_iteration):
            # 출력문 재생성
            output_text = self.summary_agent.process_with_reflection(
                origin_mail, self.self_reflection.reflection_memory
            )
            outputs.append(output_text)

            # 평가하기
            eval_result: dict = self.evaluator.get_geval_scores(origin_mail, output_text)
            eval_results.append(eval_result)
            score = round(sum(eval_result.values()) / len(eval_result), 1)

            if max_score < score:
                max_score = score
                final_output = output_text
                if round(sum(eval_result.values()) / len(eval_result), 1) >= self.threshold:
                    break

            # 점수 도달 실패 시 이유 성찰
            self.self_reflection.generate_reflection(
                origin_mail, output_text, self._create_eval_result_str(eval_result)
            )

        self._print_result(eval_results, outputs)

        return final_output

    def _create_eval_result_str(self, eval_result: dict):
        return "\n".join([f"항목: {aspect} 점수: {score}" for aspect, score in eval_result.items()])

    def _print_result(self, eval_results: list[dict], outputs: list[str]):
        max_score = 0
        final_output = ""
        max_index = 0

        for i, (eval_result, output) in enumerate(zip(eval_results, outputs)):
            score = round(sum(eval_result.values()) / len(eval_result), 1)
            print(
                f"{'=' * 25}\n"
                f"{i+1}회차 평균 {score}점\n"
                f"{self._create_eval_result_str(eval_result)}\n"
                f"Reflection 메모리:\n{self.self_reflection.get_reflection_memory_str()}\n"
                f"{'-' * 25}\n"
                f"생성된 텍스트:\n{output}\n"
                f"{'-' * 25}\n"
            )
            if max_score < score:
                max_score = score
                final_output = output
                max_index = i

        print(f"{'=' * 25}\n최종 출력:{max_index+1}회차 평균 {max_score}점\n{final_output}\n{'=' * 25}\n")
