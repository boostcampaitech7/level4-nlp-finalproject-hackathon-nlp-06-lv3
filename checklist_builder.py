import ast
import json

import pandas as pd

category_titles = {"academic": "📝 학술/연구", "administration": "🏢 행정 처리", "other": "📂 기타/그 외"}
action_titles = {"action needed": "📌 처리가 필요한 메일", "read only": "👀 읽어볼 메일"}


GMAIL_URL = "https://mail.google.com/mail/u/0/?tab=rm&ogbl#inbox/"


def build_json_checklist(df: pd.DataFrame) -> str:
    seen_message_ids = set()
    result = []

    for category, category_group in df.groupby("label_category"):
        task_objects = []
        for action, action_group in category_group.groupby("label_action"):
            items = []
            for _, row in action_group.iterrows():
                if row["message_id"] in seen_message_ids:
                    continue  # 이미 추가된 message_id는 건너뛴다.

                seen_message_ids.add(row["message_id"])

                if len(row["similar_mails"]) != 0:
                    seen_message_ids.update(row["similar_mails"])

                links = [f"{GMAIL_URL}{row['message_id']}"] + [
                    f"{GMAIL_URL}{similar_mail_id}" for similar_mail_id in row["similar_mails"]
                ]

                items.append(
                    {
                        "description": row["summary"],
                        "links": links,
                        "checked": False,
                    }
                )

            if items:
                task_objects.append({"title": action_titles[action], "items": items})

        if task_objects:
            result.append({"title": category_titles[category], "task_objects": task_objects})

    json_output = json.dumps(result, indent=4, ensure_ascii=False)

    return json_output


if __name__ == "__main__":
    df = pd.read_csv("test_mail_10.csv", index_col=0)
    df["similar_mails"] = df["similar_mails"].apply(ast.literal_eval)
    print(build_json_checklist(df))
