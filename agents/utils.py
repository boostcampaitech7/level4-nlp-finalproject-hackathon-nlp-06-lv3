import yaml

from prompt import load_template, load_template_with_variables

_YAML_FILE_PATH = "prompt/template/classification/categories.yaml"


# YAML 파일에서 카테고리 정보 로드 후 해당 레이블 명을 한글로 매핑
def map_category(english_label) -> str:
    """
    영문 카테고리 명을 한글 명으로 변경합니다.

    Args:
        english_label (_type_): 영문 카테고리 명

    Returns:
        str: 한글 카테고리 명
    """
    try:
        with open(_YAML_FILE_PATH, "r", encoding="utf-8") as file:
            categories: dict = yaml.safe_load(file)
            for category in categories:
                if category["name"] == english_label:
                    return category["korean"]
    except FileNotFoundError:
        raise FileNotFoundError(f"카테고리 파일 {_YAML_FILE_PATH}이(가) 존재하지 않습니다.")
    except yaml.YAMLError as e:
        raise ValueError(f"YAML 파일 파싱 중 오류 발생: {e}")
    return


# YAML 파일에서 카테고리 정보 로드
def load_categories_from_yaml(is_prompt: bool = False) -> list:
    """
    YAML 파일에서 카테고리 정보를 로드합니다.

    Args:
        file_path (str): YAML 파일 경로
        is_prompt (bool): True일 경우 name과 rubric만 로드하고,
                          False일 경우 name과 description만 로드합니다.
    Returns:
        list: 카테고리 정보 리스트

    Raises:
        FileNotFoundError: 파일이 존재하지 않을 경우 예외를 발생시킵니다.
        ValueError: YAML 파일 파싱 중 오류가 발생할 경우 예외를 발생시킵니다.
    """
    try:
        with open(_YAML_FILE_PATH, "r", encoding="utf-8") as file:
            categories: dict = yaml.safe_load(file)

            if is_prompt:
                return [{"name": category["name"], "rubric": category["rubric"]} for category in categories]
            else:
                return [{"name": category["name"], "description": category["description"]} for category in categories]
    except FileNotFoundError:
        raise FileNotFoundError(f"카테고리 파일 {_YAML_FILE_PATH}이(가) 존재하지 않습니다.")
    except yaml.YAMLError as e:
        raise ValueError(f"YAML 파일 파싱 중 오류 발생: {e}")


# 카테고리 정보 로드
CATEGORIES_FOR_OUTPUT = load_categories_from_yaml()

# 공통 JSON Schema 속성
MAIL_PROPERTIES = {
    "mail_id": {"type": "string", "description": "메일 ID입니다."},
    "report": {"type": "string", "description": "메일 요약문입니다."},
}


# 공통 JSON Schema 템플릿 생성 함수
def create_category_schema(categories):
    """
    카테고리 리스트를 기반으로 JSON Schema를 생성합니다.

    Args:
        categories (list): 카테고리 정보 리스트 (name, description 포함)

    Returns:
        dict: 생성된 JSON Schema
    """
    schema = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    for category in categories:
        schema["properties"][category["name"]] = {
            "type": "array",
            "description": category["description"],
            "items": {
                "type": "object",
                "properties": MAIL_PROPERTIES,
            },
        }
        schema["required"].append(category["name"])

    return schema


# 상수 정의
SUMMARY_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "email_summary",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "메일 내용의 요약문입니다.",
                }
            },
            "required": ["summary"],
        },
    },
}

REPORT_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "email_report",
        "strict": True,
        "schema": create_category_schema(CATEGORIES_FOR_OUTPUT),
    },
}

FEEDBACK_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "summary_review",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "evaluation": {
                    "type": "string",
                    "description": (
                        "요약문에 대한 평가입니다. "
                        "요약문에 문제가 없는 경우 'STOP'만 출력하고, 문제가 있는 경우 문제점(issues)을 지적하세요."
                    ),
                },
                "issues": {
                    "type": "array",
                    "description": "요약문에 개선이 필요한 경우, 식별된 문제 사항들입니다.",
                    "items": {
                        "type": "object",
                        "properties": {
                            **MAIL_PROPERTIES,
                            "issue": {
                                "type": "string",
                                "description": "요약문의 문제점입니다.",
                            },
                            "suggestion": {
                                "type": "string",
                                "description": "문제점을 개선하기 위한 수정 사항입니다.",
                            },
                        },
                        "required": ["issue", "suggestion"],
                    },
                },
            },
            "required": ["evaluation"],
        },
    },
}

REFINE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "revised_summarization",
        "strict": True,
        "schema": create_category_schema(CATEGORIES_FOR_OUTPUT),
    },
}


# 시스템 및 사용자 프롬프트 생성 함수
def build_messages(template_type: str, target_range: str, action: str, **kwargs) -> list:
    """
    OpenAI.chat.completion.create 함수에 넘겨줄 messages 인자를 생성합니다.

    Args:
        template_type (str): 템플릿이 위치한 디렉토리 유형 (예: "self_refine")
        target_range (str): 템플릿 txt 파일의 접두사 (예: "final")
        action (str): 템플릿의 용도 (예: "feedback")

    Returns:
        list: 생성된 메시지 리스트

    Raises:
        FileNotFoundError: 템플릿 파일이 존재하지 않을 경우 예외 발생
    """
    try:
        system_prompt = load_template(template_type=template_type, file_name=f"{target_range}_{action}_system.txt")
        user_prompt = load_template_with_variables(
            template_type=template_type, file_name=f"{target_range}_{action}_user.txt", **kwargs
        )
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    except FileNotFoundError as e:
        print(e)
        raise


# JSON 형식 리포트를 plain text로 변환하는 함수
def generate_plain_text_report(formatted_report: dict | str) -> str:
    """
    JSON으로 구조화된 리포트를 plain text로 변환합니다.

    Args:
        formatted_report (dict | str): JSON으로 구조화된 리포트

    Returns:
        str: plain text로 변환된 리포트
    """
    if isinstance(formatted_report, str):
        return formatted_report

    plain_text = ""
    for category, mails in formatted_report.items():
        for mail in mails:
            plain_text += f'메일 ID: {mail["mail_id"]}\n분류: {category}\n{mail["report"]}\n'

    return plain_text
