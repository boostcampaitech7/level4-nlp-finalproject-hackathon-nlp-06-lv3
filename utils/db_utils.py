import os
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import wraps

import mysql.connector
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

load_dotenv()

DB_HOST = os.getenv("MYSQL_HOST")
DB_PORT = int(os.getenv("MYSQL_PORT"))
DB_USER = os.getenv("MYSQL_USER")
DB_PASS = os.getenv("MYSQL_PASSWORD")
DB_NAME = os.getenv("MYSQL_DATABASE")

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]


@contextmanager
def db_cursor():
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        port=DB_PORT,
    )
    cursor = connection.cursor(dictionary=True)
    try:
        yield cursor
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def with_cursor(func):
    """자동으로 데이터베이스 연결과 커서를 관리하는 데코레이터"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            port=DB_PORT,
        )
        cursor = connection.cursor(dictionary=True)
        try:
            return func(cursor, *args, **kwargs)  # 커서를 함수 인자로 전달
        finally:
            connection.commit()
            cursor.close()
            connection.close()

    return wrapper


def fetch_users():
    with db_cursor() as cursor:
        cursor.execute("SELECT * FROM user_tb")
        users = cursor.fetchall()
    return users


def is_expired(expiry_time: datetime) -> bool:
    if not expiry_time:
        return True
    expiry_time = expiry_time.replace(tzinfo=timezone.utc)
    utc_current_time = datetime.now(timezone.utc)
    return utc_current_time >= expiry_time


def refresh_access_token(user_id: int, refresh_token: str) -> Credentials:
    credentials = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=SCOPES,
    )
    credentials.refresh(Request())
    with db_cursor() as cursor:
        query = "UPDATE user_tb SET access_token = %s, expiry = %s WHERE id = %s"
        cursor.execute(query, (credentials.token, credentials.expiry, user_id))

    return credentials


def authenticate_gmail(user: dict):
    refresh_token = user["refresh_token"]

    if is_expired(user["expiry"]):
        print(f"🔄 사용자 {user['id']} 토큰 만료. 새로 갱신 중...")
        creds = refresh_access_token(user["id"], refresh_token)
    else:
        creds = Credentials(
            token=user["access_token"],
            refresh_token=user["refresh_token"],
            token_uri="https://oauth2.googleapis.com/token",
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scopes=SCOPES,
        )

    print(f"✅ 사용자 {user['id']}의 인증이 완료되었습니다.")
    return build("gmail", "v1", credentials=creds)


def insert_report(user_id, report, json_checklist):
    current_datetime = datetime.now()

    with db_cursor() as cursor:
        sql = "INSERT INTO report_temp_tb (user_id, content, report, date, refresh_time) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (user_id, json_checklist, report, current_datetime.date(), current_datetime))

    print("새로운 레포트가 등록되었습니다.")
