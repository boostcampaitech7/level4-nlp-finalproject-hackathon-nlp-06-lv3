# TODO: 분류 기준이 명확할 경우에 포맷 구조 변경할 것
from prompt import load_template, load_template_with_variables

# 개별 메일 요약본의 출력 포맷팅입니다.
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

# 최종 리포트 생성에 사용되는 포맷팅입니다.
REPORT_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "email_report",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "job_related": {  # 업무 관련
                    "type": "array",
                    "description": "업무 관련 설명",
                    "items": {},
                },
                "admin_related": {  # 행정 처리
                    "type": "array",
                    "description": "행정 처리 관련 설명",
                    "items": {},
                },
                "announcement": {"type": "array", "description": "사내 소식 관련 설명", "items": {}},  # 사내 소식
            },
            "required": ["job_related", "admin_related", "announcement"],
        },
    },
}

# Self Refine의 피드백에서 사용하는 포맷팅입니다.
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
                        "요약문에 대한 평가입니다."
                        "요약문에 문제가 없는 경우 'STOP'만 출력하고, 문제가 있는 경우 문제점(issus)을 지적하세요."
                    ),
                },
                "issues": {
                    "type": "array",
                    "description": "요약문에 개선이 필요한 경우, 식별된 문제 사항들입니다.",
                    "items": {
                        "type": "object",
                        "properties": {
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

# Self Refine 내부에서 피드백을 반영할 때 사용되는 포맷팅입니다.
REFINE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "revised_summarization",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "revision": {
                    "type": "string",
                    "description": "개선 사항을 반영한 최종 요약문입니다.",
                }
            },
            "required": ["revision"],
        },
    },
}


# 시스템 및 사용자 프롬프트 생성을 모듈화하는 함수입니다.
# Agent 클래스의 process 메소드 함수에서 추론 코드를 간소화합니다.
def build_messages(template_type: str, target_range: str, action: str, **kwargs) -> list:
    """
    OpenAI.chat.completion.create 함수에 넘겨줄 messages 인자를 생성합니다.

    Args:
        template_type (str): 템플릿이 위치한 디렉토리 유형을 나타내는 문자열 (예: "self_refine")
        target_range (str): 템플릿 txt 파일의 접두사 (예: "final")
        action (str): 템플릿의 용도 (예: "feedback")

    Returns:
        list: 생성된 메세지 인자

    Notice:
        `prompt/template/{template_type}/{target_range}_{action}_system.txt`와
        `prompt/template/{template_type}/{target_range}_{action}_user.txt` 파일이 존재해야 동작합니다.
    """
    try:
        system_prompt = load_template(template_type=template_type, file_name=f"{target_range}_{action}_system.txt")
        user_prompt = load_template_with_variables(
            template_type=template_type, file_name=f"{target_range}_{action}_user.txt", **kwargs
        )
        return [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]
    except FileNotFoundError as e:
        print(e)


# Groundness Check 및 최종 리포트 생성에서 JSON 형식의 리포트를 단순 문자열로 반환하기 위한 함수입니다.
def generate_plain_text_report(formatted_report: dict) -> str:
    """
    JSON으로 구조화된 리포트를 문자열로 반환합니다.

    Args:
        formatted_report (dict): JSON으로 구조화된 리포트

    Returns:
        str: plain text로 전환한 리포트
    """

    plain_text = ""
    for label, mails in formatted_report.items():
        if label == "job_related":
            plain_text += "업무 관련\n"
        elif label == "admin_related":
            plain_text += "행정 처리\n"
        else:
            plain_text += "사내 공지"

        for mail in mails:
            plain_text += mail.summary + "\n"

    return plain_text
