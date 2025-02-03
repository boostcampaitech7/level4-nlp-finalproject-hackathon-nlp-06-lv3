import time
from datetime import datetime
from typing import Callable

import openai
import yaml
from tqdm import tqdm

from agents import map_category
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


def print_result(start_time: str, report: str, mail_dict: dict[str, Mail]):
    print("=============FINAL_REPORT================")

    elapsed_time = time.time() - start_time
    if elapsed_time > 0:
        tpm = (TokenManager.total_token_usage / elapsed_time) * 60
    else:
        tpm = 0  # 실행 시간이 0이면 0으로 처리

    print(f"실행 시간: {elapsed_time:.2f}초")
    print("평가 배제 토큰 사용 정보")
    print(f"최종 토큰 사용량: {TokenManager.total_token_usage}")
    print(f"Tokens Per Minute (TPM): {tpm:.2f}")
    print()

    for label, mail_reports in report.items():
        print(map_category(label))
        for mail_report in mail_reports:
            mail_subject = mail_dict[mail_report["mail_id"]].subject
            print(f"메일 subject: {mail_subject}")
            print(f"리포트: {mail_report['report']}")
        print()


def fetch_mails(start_date: str, end_date: str, n: int) -> dict[str, Mail]:
    messages = gmail.get_today_n_messages(start_date, n)
    mail_dict: dict[str, Mail] = {}
    for idx, message_metadata in enumerate(tqdm(messages, desc="Processing Emails")):
        # 신규 mail_id 정의: 받은 시간 순 오름차순
        mail_id = f"{end_date}/{len(messages)-idx:04d}"
        mail = Mail(message_metadata["id"], mail_id)
        # 룰베이스 분류
        if "(광고)" not in mail.subject:
            mail_dict[mail_id] = mail
    return mail_dict
