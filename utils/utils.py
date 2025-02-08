import time
from functools import wraps
from typing import Callable

import openai
import pandas as pd

from gmail_api.mail import Mail


def group_mail_dict_2_classification(mail_dict: dict[str, Mail]) -> dict[str, dict[str, Mail]]:
    """
    key: mail id, value: Mail 객체 형식의 딕셔너리를 카테고리 별로 그룹화합니다.

    Args:
        mail_dict (dict[str, Mail]): 전체 메일 정보가 담긴 딕셔너리

    Returns:
        pd.Dataframe: 카테고리 별로 그룹화된 메일 정보들

    Examples:
        실행 결과
        ```json
        {
            "academic": {
                "2025/02/01/0001": Mail,
                "2025/02/01/0002": Mail,
                ...
            },
            "administration": {...},
            "other": {...},

            # 예정
            "action needed": {...},
            "read only": {...},
        }
        ```
    """

    # TODO: 분류 기준 추가 시 데이터 파싱 변경
    grouped_df: dict[str, dict[str, Mail]] = {}
    for mail_id, mail in mail_dict.items():
        if mail.label_category not in grouped_df:
            grouped_df[mail.label_category] = {mail_id: mail}
        else:
            grouped_df[mail.label_category][mail_id] = mail

    return grouped_df


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


def retry_with_exponential_backoff(max_retry: int = 9, base_wait: int = 1):
    """
    지수 백오프 방식으로 재시도하는 데코레이터
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            wait_time = base_wait
            for attempt in range(max_retry):
                try:
                    return func(*args, **kwargs)
                except openai.RateLimitError as e:
                    print(f"[RateLimitError] 재시도 {attempt+1}/{max_retry}회: {e}")
                    if attempt < max_retry - 1:
                        time.sleep(wait_time)
                        wait_time *= 2
                    else:
                        raise e  # 최대 재시도 횟수 초과 시 에러 발생

        return wrapper

    return decorator
