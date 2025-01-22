# TODO: 분류 기준이 명확핼 경우에 포맷 구조 변경할 것
from prompt import load_template, load_template_with_variables

REPORT_FEEDBACK_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "email_report_review",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "evaluation": {
                    "type": "string",
                    "description": "Evaluation of the final report. Use 'STOP' if no issues are found, otherwise provide detailed feedback.",
                },
                "issues": {
                    "type": "array",
                    "description": "List of identified issues if the report needs improvement.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "issue": {
                                "type": "string",
                                "description": "Description of the issue identified in the report.",
                            },
                            "suggestion": {
                                "type": "string",
                                "description": "Suggested modification to resolve the issue.",
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

REPORT_REFINE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "email_summary_creation",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "final_report": {
                    "type": "string",
                    "description": "The finalized version of the email summary report with improvements applied.",
                }
            },
            "required": ["final_report"],
        },
    },
}


def create_message_arg(template_type: str, target_range: str, action: str, **kwargs) -> list:
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
