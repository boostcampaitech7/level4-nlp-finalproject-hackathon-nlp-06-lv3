import pandas as pd

from gmail_api.mail import Mail


def convert_mail_dict_to_df(mail_dict: dict[str, Mail]) -> pd.DataFrame:
    indices: list[str] = []
    data: list[dict[str, str]] = []

    for mail_id, mail in mail_dict.items():
        indices.append(mail_id)
        data.append(
            {
                "message_id": mail.message_id,
                "subject": mail.subject,
                "summary": mail.summary,
                "label_category": mail.label_category,
                "label_action": mail.label_action,
                "similar_mails": mail.similar_mails,
            }
        )

    df = pd.DataFrame(data=data, index=indices)
    df.index.name = "id"

    return df
