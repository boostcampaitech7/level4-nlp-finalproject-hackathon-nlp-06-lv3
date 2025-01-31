import argparse
import os

import yaml
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from langchain_upstage import ChatUpstage

import eval_report
import eval_summary
from agents.summary.summary_agent import SummaryAgent


def get_summaries_single_str(emails):
    """
    dict 가 담긴 list 형태를 입력값으로 받을 때 사용, 해당 dict중에서 summary만 묶어서 하나의 문자열로 전처리해준다.

    Args:
        emails (list with dicts inside)
    """
    summary_list = []
    for email in emails:
        summary_list.append(email.get("summary"))

    final = ""
    for i, summary in enumerate(summary_list):
        final += f"{i+1}.\n{summary}\n"

    return final


def load_config(config_path):
    """
    주어진 경로의 YAML 파일을 로드해 dict 형태로 반환
    """
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


class reflexion:
    def __init__(self, task, source_text, output_text):
        """
        Args:
            task (str): "single_summary" 또는 "final_report"
            source_text (str): 참조된 텍스트 (예: 원본 이메일)
            output_text (str): 생성된 텍스트 (예: 요약된 이메일)
        """

        self.task = task
        if isinstance(source_text, list) and all(isinstance(item, dict) for item in source_text):
            self.source_text = get_summaries_single_str(source_text)
        else:
            self.source_text = source_text
        self.output_text = output_text

        # Reflexion 프롬프트 템플릿을 읽어온다
        reflexion_template_name = f"reflexion_{task}.txt"
        reflexion_template_directory = f"prompt/template/reflexion/{reflexion_template_name}"
        with open(reflexion_template_directory, "r", encoding="utf-8") as file:
            self.reflection_template = file.read()

        # aspect 별 채점 기준을 읽어온다
        aspects_description_name = f"aspects_description_{task}.txt"
        reflexion_template_directory = f"prompt/template/g_eval/{aspects_description_name}"
        with open(reflexion_template_directory, "r", encoding="utf-8") as file:
            self.aspects_description = file.read()

        # reflection 을 담아줄 리스트를 선언해준다
        self.reflection_memory = []

    def initialize_chat(self, model: str, temperature=None, seed=None):
        """
        ChatUpstage 모델을 초기화합니다.

        Args:
            model (str): 사용할 모델 이름.
            temperature (float, optional): 생성 다양성을 조정하는 파라미터.
            seed (int, optional): 결과 재현성을 위한 시드 값.

        Returns:
            ChatUpstage: 초기화된 ChatUpstage 객체.
        """
        return ChatUpstage(api_key=os.getenv("UPSTAGE_API_KEY"), model=model, temperature=temperature, seed=seed)

    def evaluate(self, source_text, output_text):
        """참조한 텍스트와 생성한 텍스트를 입력으로 받고 점수를 매긴다.

        Args:
            source_text (str): 생성하는 데 참조한 텍스트
            output_text (str): 생성한 텍스트

        Returns:
            (dict, str)
            0번째는 dict, 1번째는 한 줄의 str 형식으로 aspect 별 점수를 return한다.
        """
        if self.task == "single_summary":
            run_evaluation = eval_summary.get_geval_scores
        elif self.task == "final_report":
            run_evaluation = eval_report.get_geval_scores

        parser = argparse.ArgumentParser()
        parser.add_argument("--config", default="eval_config.yml", help="Path to YAML config file")
        args = parser.parse_args()

        # Eval YAML 설정 로드
        config = load_config(args.config)

        evaluation_result = run_evaluation(source_text, output_text, config)

        return evaluation_result

    def generate_reflection(self, source_text, output_text, eval_result):
        """
        참조된 텍스트와 생성 텍스트를 입입력으로 받고 Reflection을 생성한다.

        Args:
            source_input (str): 생성할 때 참조된 텍스트
            summary_output (str): 생성된  텍스트
            eval_result (str): 평가 점수

        Returns:
            str: generated reflection
        """

        # 최종 프롬프트 선언
        prompt = PromptTemplate(
            input_variables=["source_input", "source_output", "eval_result", "eval_aspects_description"],
            template=self.reflection_template,
        )
        if not self.reflection_memory:
            previous_reflections = "없음"
        else:
            previous_reflections = "\n".join(self.reflection_memory)

        formatted_prompt = prompt.format(
            source_input=source_text,
            source_output=output_text,
            eval_result=eval_result,
            eval_aspects_description=self.aspects_description,
            previous_reflections=previous_reflections,
        )

        # ChatUpstage 모델 초기화 (필요에 따라 모델명/템퍼러쳐 변경 가능)
        chat = self.initialize_chat(model="solar-pro", temperature=0.7, seed=42)

        # 메시지 구성
        messages = [HumanMessage(content=formatted_prompt)]

        # 모델에게 메시지를 전달해 리플렉션 결과 받기
        reflection_response = chat(messages)
        reflection_text = reflection_response.content

        # 리플렉션 결과를 메모리에 추가
        self.save_reflection(reflection_text)

        # 최종 리플렉션 결과 반환
        return reflection_text

    def save_reflection(self, reflection_text):
        """reflection 메모리에 reflection을 저장한다.

        Args:
            reflection_text (str)
        """
        self.reflection_memory.append(reflection_text)

    def generate_with_reflections(self, source_text, reflections):
        if self.task == "single_summary":
            summary_type = "single"
        elif self.task == "final_report":
            summary_type = "final"

        summary_agent = SummaryAgent("solar-pro", summary_type=summary_type)
        generated_text = summary_agent.process_with_reflections(
            source_input=source_text, reflections=reflections, task=self.task
        )

        return generated_text

    def run(self, max_iteration, threshold, score_threshold):
        """
        Reflexion을 실행합니다.

        Args:
            max_iteration (float):
                루프 반복 최대 횟수입니다.
            threshold (str):
                "average": 모든 aspect 점수 평균이 threshold 점수 이상이면 루프를 종료합니다.
                "all": 모든 aspect 의 점수가 threshold 점수 이상이면 루프를 종료합니다.
            score_threshold (score_threshold):
                threshold 기준점이 되는 점수입니다.

        Returns:
            모든 aspect 점수의 평균값이 제일 높은 text가 반환됩니다.
        """
        output_text = self.output_text
        count = 1
        scores = []
        outputs = []
        print("=" * 25)
        print("INITIATE REFLEXION")
        print("=" * 25)
        while True:
            # 평가하기
            eval_result_dict, eval_result_str = self.evaluate(self.source_text, output_text)

            # 성찰하기
            new_reflection = self.generate_reflection(
                source_text=self.source_text, output_text=output_text, eval_result=eval_result_str
            )
            # 재생성하기
            previous_reflections = "\n".join(self.reflection_memory)
            output_text = self.generate_with_reflections(source_text=self.source_text, reflections=previous_reflections)

            eval_average = round(sum(eval_result_dict.values()) / len(eval_result_dict.values()), 1)
            scores.append(eval_average)
            outputs.append(output_text)

            print("=" * 25)
            print(f"{count}회차")
            print("-" * 25)
            print(f"{eval_result_str}, 평균 {eval_average}점")
            print("-" * 25)
            print(f"Reflection 메모리:\n{previous_reflections}")
            print("-" * 25)
            print(f"성찰 후 재생성된 텍스트:\n{output_text}")
            print("-" * 25)

            if threshold == "all" and all(value > score_threshold for value in eval_result_dict.values()):
                print("=" * 25)
                print("Evaluation 점수 만족, Reflexion 루프 종료")
                break
            elif threshold == "average" and eval_average >= score_threshold:
                print("=" * 25)
                print("Evaluation 점수 만족, Reflexion 루프 종료")
                break
            elif count >= max_iteration:
                break

            count += 1

        for i, score in enumerate(scores):
            print(f"{i+1}회차 평균 {score}점")
        print("\n최종")
        final = outputs[scores.index(max(scores))]

        return final
