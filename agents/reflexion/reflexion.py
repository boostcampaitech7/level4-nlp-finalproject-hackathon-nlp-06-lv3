from utils.utils import map_category, run_with_retry

from ..summary import SummaryAgent
from .evaluator import ReflexionEvaluator
from .self_reflection import ReflexionSelfReflection


class ReflexionFramework:
    def __init__(self, model_name: str, task: str, config: dict):
        self.task = task
        self.evaluator = ReflexionEvaluator(task)
        self.self_reflection = ReflexionSelfReflection(task)
        self.config = config

    def preprocess_actor_output(self, actor_output):
        output_text = ""
        for label, mail_reports in actor_output.items():
            output_text += f"{map_category(label)}\n"
            count_emails = 1
            for mail_report in mail_reports:
                output_text += f"{count_emails}. {mail_report['report']}\n"
                count_emails += 1
            output_text += "\n\n"

        return output_text

    def process(self, origin_mail, model: SummaryAgent) -> tuple[str, int]:
        """
        Reflexion을 실행합니다.

        Args:

        Returns:
            모든 aspect 점수의 평균값이 제일 높은 text가 반환됩니다.
        """
        threshold_type = self.config["self_reflection"]["reflexion"]["threshold_type"]
        threshold = self.config["self_reflection"]["reflexion"]["threshold"]

        self.self_reflection.load_setup_texts()

        scores = []
        outputs = []
        output_text, _ = run_with_retry(model.process, origin_mail)
        output_text = output_text["summary"]
        total_token_usage = 0
        for i in range(self.config["self_reflection"]["max_iteration"]):
            # 평가하기
            eval_result_list, eval_token_usage = self.evaluator.get_geval_scores(origin_mail, output_text)
            eval_result_str = ""
            aspect_score = 0
            for eval_result in eval_result_list:
                aspect_len = len(eval_result)
                for aspect, score in eval_result.items():
                    eval_result_str += f"항목: {aspect} 점수: {score}\n"
                    aspect_score += score
            total_token_usage += eval_token_usage

            # 성찰하기
            _, reflection_token_usage = run_with_retry(
                self.self_reflection.generate_reflection, origin_mail, output_text, eval_result_str
            )
            total_token_usage += reflection_token_usage

            # 출력문 다시 생성하기
            previous_reflections = self.self_reflection.reflection_memory
            output_text, token_usage = run_with_retry(model.process, origin_mail, 3, previous_reflections)
            total_token_usage += token_usage

            eval_average = round(aspect_score / aspect_len, 1)
            scores.append(eval_average)
            outputs.append(output_text["summary"])
            previous_reflections_msg = "\n".join(previous_reflections)
            print(
                "\n\nINITIALIZE REFLEXION\n"
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

        return final, total_token_usage

    def process_with_solar_as_judge(self, mail, model: SummaryAgent, config: dict):
        source_text_str = str(mail)
        check_results = []
        scores = []
        outputs = []
        output_text = run_with_retry(model.process, mail)
        total_token_usage = 0
        print("\n\nINITIATE REFLEXION w/ Solar as Judge\n")
        for i in range(config["self_reflection"]["max_iteration"]):
            # 평가하기
            solar_as_judge_result = self.evaluator.get_solar_as_judge_result(source_text_str, output_text)
            items_failed = []
            for key, value in solar_as_judge_result.items():
                if value == 0:
                    items_failed.append(key)
            check_results.append(solar_as_judge_result)
            score = list(solar_as_judge_result.values()).count(1)
            scores.append(score)

            items_failed_str = "\n".join(items_failed)
            # print(f"{type(source_text_str)}")
            # print(f"{type(output_text)}")
            # print(f"{type(items_failed_str)}")
            # 성찰하기
            _, reflection_token_usage = run_with_retry(
                self.self_reflection.generate_reflection_solar_as_judge, source_text_str, output_text, items_failed_str
            )
            total_token_usage += reflection_token_usage

            # 출력문 다시 생성하기
            previous_reflections = self.self_reflection.reflection_memory
            output_text, token_usage = run_with_retry(model.process, mail, 3, previous_reflections)
            total_token_usage += token_usage

            outputs.append(output_text)

            previous_reflections_str = "\n".join(previous_reflections)

            print(
                f"{'=' * 25}\n"
                f"{i + 1}회차\n"
                f"{'-' * 25}\n"
                f"통과 항목 {score}개\n"
                f"탈락 항목:\n{items_failed_str}\n"
                f"{'-' * 25}\n"
                f"Reflection 메모리:\n{previous_reflections_str}\n\n"
                f"{'-' * 25}\n"
                f"성찰 후 재생성된 텍스트:\n{output_text}"
            )

            if score == len(solar_as_judge_result):
                print(f"{'=' * 25}\n" "Evaluation 점수 만족, Reflexion 루프 종료\n" f"{'=' * 25}")
                break

        for i, score in enumerate(scores):
            print(f"{i+1}회차 평균 {score}점")

        print(f"\n최종 출력문 ({scores.index(max(scores)) + 1}회차, 평균: {max(scores)}점)")
        final = outputs[scores.index(max(scores))]
        print(f"{final}")

        return final, total_token_usage
