# 공통 JSON Schema 속성
MAIL_PROPERTIES = {
    "mail_id": {"type": "string", "description": "메일 ID입니다."},
    "report": {"type": "string", "description": "메일 요약문입니다."},
}

# 상수 정의
# SUMMARY_FORMAT = {
#     "type": "json_schema",
#     "json_schema": {
#         "name": "email_summary",
#         "strict": True,
#         "schema": {
#             "type": "object",
#             "properties": {
#                 "summary": {
#                     "type": "string",
#                     "description": "메일 내용의 요약문입니다.",
#                 }
#             },
#             "required": ["summary"],
#         },
#     },
# }

""" 최종 report refine 적용하지 않게 되며 불필요해진 부분 일부 주석처리
REPORT_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "email_report",
        "strict": True,
        "schema": create_category_schema(CATEGORIES_FOR_OUTPUT),
    },
}
"""
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
            "required": ["evaluation", "issues"],
        },
    },
}

"""  최종 report refine 적용하지 않게 되며 불필요해진 부분 일부 주석처리
REFINE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "revised_summarization",
        "strict": True,
        "schema": create_category_schema(CATEGORIES_FOR_OUTPUT),
    },
}
"""
