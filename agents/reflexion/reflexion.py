from agents.reflexion.evaluator import ReflexionEvaluator
from agents.reflexion.self_reflection import ReflexionSelfReflection
from agents.summary.summary_agent import SummaryAgent
from utils.configuration import Config


class ReflexionFramework:
    def __init__(self):
        self.evaluator = ReflexionEvaluator()
        self.self_reflection = ReflexionSelfReflection()
        self.threshold_type = Config.config["reflexion"]["threshold_type"]
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

        output_text = summary_agent.process_with_reflection(origin_mail)
        print("\n\nINITIATE REFLEXION\n")
        print(f"{'=' * 25}\n" f"초기 출력문:\n{output_text}\n" f"{'=' * 25}\n")

        for i in range(self.max_iteration):
            # 평가하기
            eval_result: dict = self.evaluator.get_geval_scores(origin_mail, output_text)
            eval_result_str = "\n".join([f"항목: {aspect} 점수: {score}" for aspect, score in eval_result.items()])
            aspect_score = sum(eval_result.values())

            # 성찰하기
            self.self_reflection.generate_reflection(origin_mail, output_text, eval_result_str)

            # 출력문 다시 생성하기
            previous_reflections = self.self_reflection.reflection_memory
            output_text = summary_agent.process_with_reflection(origin_mail, 3, previous_reflections)

            eval_average = round(aspect_score / len(eval_result), 1)
            scores.append(eval_average)
            outputs.append(output_text)
            previous_reflections_msg = "\n".join(previous_reflections)
            print(
                f"{'=' * 25}\n"
                f"{i + 1}회차\n"
                f"{'-' * 25}\n"
                f"{eval_result_str}, 평균 {eval_average}점\n"
                f"{'-' * 25}\n"
                f"Reflection 메모리:\n{previous_reflections_msg}\n\n"
                f"{'-' * 25}\n"
                f"성찰 후 재생성된 텍스트:\n{output_text}"
            )

            if (self.threshold_type == "all" and all(value > self.threshold for value in scores)) or (
                self.threshold_type == "average" and eval_average >= self.threshold
            ):
                print(f"{'=' * 25}\n" "Evaluation 점수 만족, Reflexion 루프 종료\n" f"{'=' * 25}")
                break

        for i, score in enumerate(scores):
            print(f"{i+1}회차 평균 {score}점")
        print("=" * 25)
        print(f"\n최종 출력문 ({scores.index(max(scores)) + 1}회차, 평균: {max(scores)}점)")
        final = outputs[scores.index(max(scores))]
        print(f"{final}")

        return final
