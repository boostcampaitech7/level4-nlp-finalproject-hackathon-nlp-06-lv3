import json
from collections import defaultdict

category_titles = {"academic": "📝 학술/연구", "administration": "🏢 행정 처리", "other": "📂 기타/그 외"}
action_titles = {"action needed": "📌 처리가 필요한 메일", "read only": "👀 읽어볼 메일"}


GMAIL_URL = "https://mail.google.com/mail/u/0/?tab=rm&ogbl#inbox/"
CATEGORY_ORDER = ["academic", "administration", "other"]
ACTION_ORDER = ["action needed", "read only"]


def build_json_checklist(
    summary_dict: dict[str, str],
    category_dict: dict[str, str],
    action_dict: dict[str, str],
    similar_mails_dict: dict[str, list[str]],
) -> str:
    seen_message_ids = set()
    result = defaultdict(lambda: defaultdict(list))

    for mail_id, summary in summary_dict.items():
        if mail_id in seen_message_ids:
            continue

        seen_message_ids.add(mail_id)
        seen_message_ids.update(similar_mails_dict.get(mail_id, []))

        category = category_dict.get(mail_id, "other")
        action = action_dict.get(mail_id, "read only")

        links = [f"{GMAIL_URL}{mail_id}"] + [
            f"{GMAIL_URL}{similar_mail_id}" for similar_mail_id in similar_mails_dict.get(mail_id, [])
        ]

        result[category][action].append(
            {
                "description": summary,
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
