import time
from datetime import datetime, timedelta
from typing import Callable

import openai
import pandas as pd
import pytz
import yaml
from tqdm import tqdm

from agents import ClassificationType
from gmail_api import Mail
from gmail_api.gmail_process import gmail


class TokenManager:
    total_token_usage = 0


def load_config(config_path="config.yml"):
    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    config["gmail"]["start_date"] = "2025/01/10" if not config["gmail"]["start_date"] else config["gmail"]["start_date"]
    config["gmail"]["end_date"] = (
        datetime.now().strftime("%Y/%m/%d") if not config["gmail"]["end_date"] else config["gmail"]["end_date"]
    )

    return config


def run_with_retry(func: Callable, *args, max_retry=9, base_wait=1):
    """
    지수 백오프 방식으로 재시도하는 헬퍼 함수
    """
    wait_time = base_wait
    for attempt in range(max_retry):
        try:
            return func(*args)
        except openai.RateLimitError as e:
            print(f"[RateLimitError] 재시도 {attempt+1}/{max_retry}회: {e}")
            if attempt < max_retry - 1:
                time.sleep(wait_time)
                wait_time *= 2
            else:
                # 최대 재시도 횟수를 초과하면 에러를 다시 던짐
                raise e


def map_category(classification_type: str, english_label: str) -> str:
    """
    영문 카테고리 명을 한글 명으로 변경합니다.

    Args:
        english_label (_type_): 영문 카테고리 명

    Returns:
        str: 한글 카테고리 명
    """
    yaml_file_path = f"prompt/template/classification/{classification_type}.yaml"

    try:
        with open(yaml_file_path, "r", encoding="utf-8") as file:
            categories: dict = yaml.safe_load(file)
            for category in categories:
                if category["name"] == english_label:
                    return category["korean"]
    except FileNotFoundError:
        raise FileNotFoundError(f"카테고리 파일 {yaml_file_path}이(가) 존재하지 않습니다.")
    except yaml.YAMLError as e:
        raise ValueError(f"YAML 파일 파싱 중 오류 발생: {e}")
    return


def print_result(start_time: str, mail_dict: dict[str, Mail]):
    print("=============FINAL_REPORT================")

    elapsed_time = time.time() - start_time
    if elapsed_time > 0:
        tpm = (TokenManager.total_token_usage / elapsed_time) * 60
    else:
        tpm = 0  # 실행 시간이 0이면 0으로 처리

    print(
        f"실행 시간: {elapsed_time:.2f}초"
        "평가 배제 토큰 사용 정보"
        f"최종 토큰 사용량: {TokenManager.total_token_usage}"
        f"Tokens Per Minute (TPM): {tpm:.2f}\n"
    )

    for mail_id, mail in mail_dict.items():
        sim_mails_str = "\n".join(
            [
                f"\t{i + 1}번째 유사 메일\n"
                f"\tID: {sim_mail_id}\n"
                f"\t제목: {mail_dict[sim_mail_id].subject}\n"
                f"\t요약: {mail_dict[sim_mail_id].summary}\n"
                for i, sim_mail_id in enumerate(mail.similar_mails)
            ]
        )

        print(
            f"ID: {mail_id}\n"
            f"분류 1: {map_category(ClassificationType.CATEGORY,mail.label_category)}\n"
            f"분류 2: {map_category(ClassificationType.ACTION,mail.label_action)}\n"
            f"제목: {mail.subject}\n"
            f"요약: {mail.summary}\n"
            f"{sim_mails_str}\n"
            f"{'=' * 40}\n\n"
        )


def get_yesterday_9am() -> datetime:
    # 서울 시간 기준, 전일의 오전 9시 datetime객체를 반환합니다.
    seoul_tz = pytz.timezone("Asia/Seoul")
    now = datetime.now(seoul_tz)
    yesterday = now - timedelta(days=1)
    return datetime(yesterday.year, yesterday.month, yesterday.day, 9, 0, 0, tzinfo=seoul_tz)


def is_before_yesterday_9am(date_str: str, yesterday_9am: datetime) -> bool:
    # 인자의 날짜가 전일 9시 이전이면 True, 이후이면 False를 반환합니다.
    date = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
    seoul_tz = pytz.timezone("Asia/Seoul")
    date_in_seoul = date.astimezone(seoul_tz)
    return date_in_seoul < yesterday_9am


def fetch_mails(start_date: str, end_date: str, n: int) -> dict[str, Mail]:
    messages = gmail.get_today_n_messages(start_date, n)
    mail_dict: dict[str, Mail] = {}
    yesterday_9am = get_yesterday_9am()

    for idx, message_metadata in enumerate(tqdm(messages, desc="Processing Emails")):
        # 신규 mail_id 정의: 받은 시간 순 오름차순
        mail_id = f"{end_date}/{len(messages)-idx:04d}"
        mail = Mail(message_metadata["id"], mail_id)
        if is_before_yesterday_9am(mail.date, yesterday_9am):
            pass  # break 실제 실행 시에는 break 하여 더 이상 메일을 처리하지 않음

        # TODO: 룰베이스 분류 강화
        if "(광고)" not in mail.subject:
            mail_dict[mail_id] = mail

    print(f"🕊️  전일 오전 9시 이후 수신한 메일 {len(mail_dict)}개를 저장하였습니다.")
    return mail_dict


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
