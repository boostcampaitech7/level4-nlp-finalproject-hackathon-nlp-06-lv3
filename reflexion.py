import argparse
import json

import yaml
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from langchain_upstage import ChatUpstage
from openai import OpenAI

import eval_report
import eval_summary
from agents import BaseAgent, check_groundness
from agents.utils import REPORT_FORMAT, SUMMARY_FORMAT, build_messages, generate_plain_text_report
from gmail_api import Mail
from utils.utils import map_category


class ReflexionActorSummaryAgent(BaseAgent):
    """
    SummaryAgent는 기본적으로 이메일과 같은 텍스트 데이터를 요약하기 위한 에이전트 클래스입니다.
    Reflexion 프레임워크 안에서는 저장된 Reflection을 프롬프트에 넣는 단계가 추가 됐습니다.
    내부적으로 Upstage 플랫폼의 ChatUpstage 모델을 사용하여 요약 작업을 수행합니다.

    Args:
        model_name (str): 사용할 Upstage AI 모델명입니다(예: 'solar-pro', 'solar-mini').
        summary_type (str): 요약 유형을 지정하는 문자열입니다(예: 'final', 'single' 등).
        temperature (float, optional): 모델 생성에 사용되는 파라미터로, 0에 가까울수록
            결정론적(deterministic) 결과가, 1에 가까울수록 다양성이 높은 결과가 나옵니다.
        seed (int, optional): 모델 결과의 재현성을 높이기 위해 사용하는 난수 시드 값입니다.

    Attributes:
        summary_type (str): 요약 유형을 나타내는 문자열입니다.
    """

    def __init__(self, model_name: str, summary_type: str, temperature=None, seed=None, api_key=None):
        super().__init__(model=model_name, temperature=temperature, seed=seed)

        # SummaryAgent 객체 선언 시 summary_type을 single|final로 강제합니다.
        if summary_type != "single" and summary_type != "final":
            raise ValueError(
                f'summary_type: {summary_type}는 허용되지 않는 인자입니다. "single" 혹은 "final"로 설정해주세요.'
            )

        # 추후 프롬프트 템플릿 로드 동작을 위해 string으로 받아 attribute로 저장합니다.
        self.summary_type = summary_type
        self.api_key = api_key

    def initialize_chat(self, model: str, temperature=None, seed=None):
        """
        요약을 위해 OpenAI 모델 객체를 초기화합니다.

        Args:
            model (str): 사용할 모델 이름.
            temperature (float, optional): 생성 다양성을 조정하는 파라미터.
            seed (int, optional): 결과 재현성을 위한 시드 값.

        Returns:
            OpenAI: 초기화된 Solar 모델 객체.
        """
        return OpenAI(api_key=self.api_key, base_url="https://api.upstage.ai/v1/solar")

    def process(self, mail: dict[Mail] | Mail, max_iteration: int = 3, reflections: list = []) -> dict:
        """
        주어진 메일(또는 메일 리스트)을 요약하여 JSON 형태로 반환합니다.
        내부적으로는 미리 정의된 템플릿과 결합하여 Solar 모델에 요약 요청을 보냅니다.

        Args:
            mail (dict[Mail] | Mail): 요약할 메일 객체(Mail) 또는 문자열 리스트입니다.
            max_iteration (int): 최대 Groundness Check 횟수입니다.
            reflections (list): 문자열 형태의 Reflection들을 담은 리스트입니다.

        Returns:
            dict: 요약된 결과 JSON입니다.
        """
        # self.summary_type에 따라 데이터 유효 검증 로직
        if (self.summary_type == "single" and not isinstance(mail, Mail)) or (
            self.summary_type == "final" and not isinstance(mail, dict)
        ):
            raise ValueError(f"{self.summary_type}.process의 mail로 잘못된 타입의 데이터가 들어왔습니다.")

        # 출력 포맷 지정
        response_format = SUMMARY_FORMAT if self.summary_type == "single" else REPORT_FORMAT

        # LLM 입력을 위한 문자열 처리
        input_mail_data = ""
        # if self.summary_type == "single":
        #     input_mail_data = str(mail)
        # else:
        #     input_mail_data = "\n".join(
        #         [f"메일 id: {item.id} 분류: {item.label} 요약문: {item.summary}" for _, item in mail.items()]
        #     )

        if self.summary_type == "single":
            input_mail_data = str(mail)
        else:
            input_mail_data = ""
            count = 1
            for _, item in mail.items():
                input_mail_data += f"{count}번 이메일 (분류: {item.label}) {item.summary}\n"
                count += 1

        # 리스트 안에 담긴 reflection들 문자열 형태로 처리, 없으면 "제공된 피드백 없음" 으로 처리
        if not reflections:
            input_reflections = "제공된 피드백 없음"
        else:
            input_reflections = "\n".join(reflections)

        # max_iteration 번 Groundness Check 수행
        for i in range(max_iteration):
            if self.summary_type == "single":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    # ./prompt/template/summary/{self.summary_type}_summary_system(혹은 user).txt 템플릿에서 프롬프트 생성
                    messages=build_messages(
                        template_type="reflexion",
                        target_range=self.summary_type,
                        action="summary_reflexion",
                        mail=input_mail_data,
                        previous_reflections=input_reflections,
                    ),
                    response_format=response_format,
                )
            elif self.summary_type == "final":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    # ./prompt/template/summary/{self.summary_type}_summary_system(혹은 user).txt 템플릿에서 프롬프트 생성
                    messages=build_messages(
                        template_type="reflexion",
                        target_range=self.summary_type,
                        action="report_reflexion",
                        mail=input_mail_data,
                        previous_reflections=input_reflections,
                    ),
                    response_format=response_format,
                )
            summarized_content: dict = json.loads(response.choices[0].message.content)

            # Groundness Check를 위해 JSON 결과에서 문자열 정보 추출
            if self.summary_type == "single":
                result = summarized_content["summary"]
            else:
                result = generate_plain_text_report(summarized_content)

            # Groundness Check
            groundness = check_groundness(context=input_mail_data, answer=result, api_key=self.api_key)
            print(f"{i + 1}번째 사실 확인: {groundness}")
            if groundness == "grounded":
                break
        return summarized_content

    @staticmethod
    def calculate_token_cost():
        pass


class ReflexionEvaluator:
    def __init__(self, task):
        self.task = task

    def get_geval_scores(self, source_text, output_text):
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


class ReflexionSelfReflection:
    def __init__(self, task, api_key):
        # Reflection을 담을 리스트를 선언해준다
        self.reflection_memory = []
        self.reflection_template = None
        self.aspects_description = None
        self.task = task
        self.api_key = api_key

    def load_setup_texts(self):
        # Reflexion 프롬프트 템플릿을 읽어온다
        reflexion_template_name = f"reflexion_{self.task}.txt"
        reflexion_template_directory = f"prompt/template/reflexion/{reflexion_template_name}"
        with open(reflexion_template_directory, "r", encoding="utf-8") as file:
            self.reflection_template = file.read()

        # aspect 별 채점 기준을 읽어온다
        aspects_description_name = f"aspects_description_{self.task}.txt"
        reflexion_template_directory = f"prompt/template/g_eval/{aspects_description_name}"
        with open(reflexion_template_directory, "r", encoding="utf-8") as file:
            self.aspects_description = file.read()

    def save_reflection(self, reflection_text):
        """reflection 메모리에 reflection을 저장한다.

        Args:
            reflection_text (str)
        """
        self.reflection_memory.append(reflection_text)

    def initialize_chat(self, model: str, temperature=None, seed=None):
        """
        요약을 위해 OpenAI 모델 객체를 초기화합니다.

        Args:
            model (str): 사용할 모델 이름.
            temperature (float, optional): 생성 다양성을 조정하는 파라미터.
            seed (int, optional): 결과 재현성을 위한 시드 값.

        Returns:
            OpenAI: 초기화된 Solar 모델 객체.
        """
        return ChatUpstage(api_key=self.api_key, model=model, temperature=temperature, seed=seed)

    def generate_reflection(self, source_text, output_text, eval_result):
        """
        참조된 텍스트와 생성 텍스트를 입력으로 받고 Reflection을 생성한다.

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


class ReflexionFramework:
    def __init__(self, task, actor, evaluator, self_reflection):

        if task != "single_summary" and task != "final_report":
            raise ValueError(
                f'summary_type: {task}는 허용되지 않는 인자입니다. "single_summary" 혹은 "final_report"로 설정해주세요.'
            )

        actor_class = (ReflexionActorSummaryAgent,)
        evaluator_class = ReflexionEvaluator
        self_reflection_class = ReflexionSelfReflection

        # 타입 체크
        if not isinstance(actor, actor_class):
            raise TypeError(f"Actor class must be {actor_class.__name__}, input:{type(actor).__name__}")

        if not isinstance(evaluator, evaluator_class):
            raise TypeError(f"Evaluator class must be {evaluator_class.__name__}, input:{type(evaluator).__name__}")

        if not isinstance(self_reflection, self_reflection_class):
            raise TypeError(
                f"SelfReflection class must be {self_reflection_class.__name__}, input:{type(self_reflection).__name__}"
            )

        self.task = task
        self.actor = actor
        self.evaluator = evaluator
        self.self_reflection = self_reflection

    def preprocess_actor_output(self, task, actor_output):
        if task == "final_report":
            output_text = ""
            for label, mail_reports in actor_output.items():
                output_text += f"{map_category(label)}\n"
                count_emails = 1
                for mail_report in mail_reports:
                    output_text += f"{count_emails}. {mail_report['report']}\n"
                    count_emails += 1
                output_text += "\n\n"
        elif task == "single_summary":
            output_text = actor_output.get("summary")

        return output_text

    def run(self, source_text, initial_output_text, max_iteration, threshold, score_threshold):
        """
        Reflexion을 실행합니다.

        Args:

            source_text (dict[Mail] | Mail) = 원본 참고 텍스트
            output_text (str) = 최초 출력 텍스트
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
        self.self_reflection.load_setup_texts()

        # if self.task == "single_summary":
        #     source_text_str = str(source_text)
        # else:
        #     source_text_str = "\n".join(
        #         [f"메일 id: {item.id} 분류: {item.label} 요약문: {item.summary}" for _, item in source_text.items()]
        #     )

        if self.task == "single_summary":
            source_text_str = str(source_text)
        else:
            source_text_str = ""
            count = 1
            for _, item in source_text.items():
                source_text_str += f"{count}번 이메일 (분류: {item.label}) {item.summary}\n"
                count += 1

        loop_count = 1
        scores = []
        outputs = []
        output_text = initial_output_text

        while True:
            # 평가하기
            eval_result_dict, eval_result_str = self.evaluator.get_geval_scores(source_text_str, output_text)

            # 성찰하기
            self.self_reflection.generate_reflection(
                source_text=source_text_str, output_text=output_text, eval_result=eval_result_str
            )

            # 출력문 다시 생성하기
            previous_reflections = self.self_reflection.reflection_memory
            actor_output = self.actor.process(mail=source_text, max_iteration=3, reflections=previous_reflections)

            # SummaryAgent에서 나온 출력물을 Evaluator, SelfReflection에 전달해주기 위해 전처리
            output_text = self.preprocess_actor_output(task=self.task, actor_output=actor_output)

            eval_average = round(sum(eval_result_dict.values()) / len(eval_result_dict.values()), 1)
            scores.append(eval_average)
            outputs.append(output_text)
            previous_reflections_msg = "\n".join(previous_reflections)
            print("\n\nINITIALIZE REFLEXION")
            print("=" * 25)
            print(f"{loop_count}회차")
            print("-" * 25)
            print(f"{eval_result_str}, 평균 {eval_average}점")
            print("-" * 25)
            print(f"Reflection 메모리:\n{previous_reflections_msg}")
            print("-" * 25)
            print(f"성찰 후 재생성된 텍스트:\n{output_text}")

            if threshold == "all" and all(value > score_threshold for value in eval_result_dict.values()):
                print("=" * 25)
                print("Evaluation 점수 만족, Reflexion 루프 종료")
                print("=" * 25)
                break
            elif threshold == "average" and eval_average >= score_threshold:
                print("=" * 25)
                print("Evaluation 점수 만족, Reflexion 루프 종료")
                print("=" * 25)
                break
            elif loop_count >= max_iteration:
                print("=" * 25)
                print("Reflexion 루프 종료")
                print("=" * 25)
                break

            loop_count += 1

        for i, score in enumerate(scores):
            print(f"{i+1}회차 평균 {score}점")
        print("=" * 25)
        print(f"\n최종 출력문 ({scores.index(max(scores)) + 1}회차, 평균: {max(scores)}점)")
        final = outputs[scores.index(max(scores))]
        print(f"{final}")

        return final


def load_config(config_path):
    """
    주어진 경로의 YAML 파일을 로드해 dict 형태로 반환
    """
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


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
