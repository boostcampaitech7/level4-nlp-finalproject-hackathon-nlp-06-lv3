from agents.reflexion.evaluator import ReflexionEvaluator
from agents.reflexion.self_reflection import ReflexionSelfReflection
from agents.summary.summary_agent import SummaryAgent
from utils.configuration import Config


class ReflexionFramework:
    def __init__(self):
        self.evaluator = ReflexionEvaluator()
        self.self_reflection = ReflexionSelfReflection()
        self.threshold = Config.config["reflexion"]["threshold"]
        self.max_iteration = Config.config["reflexion"]["max_iteration"]

    def process(self, origin_mail, summary_agent: SummaryAgent) -> str:
        """
        Reflexion을 실행합니다.

        Args:

        Returns:
            모든 aspect 점수의 평균값이 제일 높은 text가 반환됩니다.
        """
        scores = []
        outputs = []

        for i in range(self.max_iteration):
            # 출력문 재생성
            output_text = summary_agent.process_with_reflection(origin_mail, self.self_reflection.reflection_memory)
            outputs.append(output_text)

            # 평가하기
            eval_result: dict = self.evaluator.get_geval_scores(origin_mail, output_text)
            scores.append(round(sum(eval_result.values()) / len(eval_result), 1))

            eval_average = round(sum(eval_result.values()) / len(eval_result), 1)
            self._print_reflection_process(eval_result, output_text, eval_average)

            if eval_average >= self.threshold:
                break

            # 점수 도달 실패 시 이유 성찰
            self.self_reflection.generate_reflection(
                origin_mail, output_text, self._create_eval_result_str(eval_result)
            )

        self._print_result(scores, outputs)

        _, final_output = max(zip(scores, outputs), key=lambda x: x[0])

        return final_output

    def _create_eval_result_str(self, eval_result: dict):
        return "\n".join([f"항목: {aspect} 점수: {score}" for aspect, score in eval_result.items()])

    def _print_reflection_process(self, eval_result: dict, output_text: str, score: float):
        print(
            f"{'=' * 25}\n"
            f"Reflection 메모리:\n{self.self_reflection.get_reflection_memory_str()}\n\n"
            f"{'-' * 25}\n"
            f"생성된 텍스트:\n{output_text}"
            f"{'-' * 25}\n"
            f"{self._create_eval_result_str(eval_result)}, 평균 {score}점\n"
        )

    def _print_result(self, scores, outputs):
        for i, score in enumerate(scores):
            print(f"{i+1}회차 평균 {score}점")
        print(f"{'='*25}\n")
        best_index = max(enumerate(scores), key=lambda x: x[1])[0]
        print(f"최종 출력문 ({best_index + 1}회차, 평균: {scores[best_index]}점)")
        print(outputs[best_index])
