import json
from collections import defaultdict

from gmail_api.mail import Mail

category_titles = {"academic": "📝 학술/연구", "administration": "🏢 행정 처리", "other": "📂 기타/그 외"}
action_titles = {"action needed": "📌 처리가 필요한 메일", "read only": "👀 읽어볼 메일"}


GMAIL_URL = "https://mail.google.com/mail/u/0/?tab=rm&ogbl#inbox/"
CATEGORY_ORDER = ["academic", "administration", "other"]
ACTION_ORDER = ["action needed", "read only"]


def build_json_checklist(mail_dict: dict[str, Mail]) -> str:
    seen_message_ids = set()
    result = defaultdict(lambda: defaultdict(list))

    for mail in mail_dict.values():
        if mail.message_id in seen_message_ids:
            continue

        seen_message_ids.add(mail.message_id)
        seen_message_ids.update(mail.similar_mails)

        links = [f"{GMAIL_URL}{mail.message_id}"] + [
            f"{GMAIL_URL}{similar_mail_id}" for similar_mail_id in mail.similar_mails
        ]

        result[mail.label_category][mail.label_action].append(
            {
                "description": mail.summary,
                "links": links,
                "checked": False,
            }
        )

    json_output = [
        {
            "title": category_titles[category],
            "task_objects": [
                {"title": action_titles[action], "items": result[category][action]}
                for action in ACTION_ORDER
                if result[category][action]  # 액션이 있는 경우만 추가
            ],
        }
        for category in CATEGORY_ORDER
        if category in result  # 카테고리가 있는 경우만 추가
    ]

    return json.dumps(json_output, indent=4, ensure_ascii=False)
