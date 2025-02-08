from agents.reflexion.evaluator import ReflexionEvaluator
from agents.reflexion.self_reflection import ReflexionSelfReflection
from agents.summary.summary_agent import SummaryAgent


class ReflexionFramework:
    def __init__(self, model_name: str, task: str, config: dict):
        self.task = task
        self.evaluator = ReflexionEvaluator(task)
        self.self_reflection = ReflexionSelfReflection(task)
        self.config = config

    def process(self, origin_mail, summary_agent: SummaryAgent) -> str:
        """
        Reflexion을 실행합니다.

        Args:

        Returns:
            모든 aspect 점수의 평균값이 제일 높은 text가 반환됩니다.
        """
        threshold_type = self.config["self_reflection"]["reflexion"]["threshold_type"]
        threshold = self.config["self_reflection"]["reflexion"]["threshold"]

        scores = []
        outputs = []
        initail_content = summary_agent.process(origin_mail, 3, ["start"])
        output_text = initail_content["summary"]
        print("\n\nINITIATE REFLEXION\n")
        for i in range(self.config["self_reflection"]["max_iteration"]):
            # 평가하기
            eval_result_list = self.evaluator.get_geval_scores(origin_mail, output_text)
            eval_result_str = ""
            aspect_score = 0
            for eval_result in eval_result_list:
                aspect_len = len(eval_result)
                for aspect, score in eval_result.items():
                    eval_result_str += f"항목: {aspect} 점수: {score}\n"
                    aspect_score += score

            # 성찰하기
            self.self_reflection.generate_reflection(origin_mail, output_text, eval_result_str)

            # 출력문 다시 생성하기
            previous_reflections = self.self_reflection.reflection_memory
            output_text = summary_agent.process(origin_mail, 3, previous_reflections)

            eval_average = round(aspect_score / aspect_len, 1)
            scores.append(eval_average)
            outputs.append(output_text["summary"])
            previous_reflections_msg = "\n".join(previous_reflections)
            print(
                f"{'=' * 25}\n"
                f"{i + 1}회차\n"
                f"{'-' * 25}\n"
                f"{eval_result_str}, 평균 {eval_average}점\n"
                f"{'-' * 25}\n"
                f"Reflection 메모리:\n{previous_reflections_msg}\n\n"
                f"{'-' * 25}\n"
                f"성찰 후 재생성된 텍스트:\n{output_text['summary']}"
            )

            if (threshold_type == "all" and all(value > threshold for value in scores)) or (
                threshold_type == "average" and eval_average >= threshold
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
