import os
from datetime import datetime, timezone

import mysql.connector
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from mysql.connector.abstracts import MySQLConnectionAbstract

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


def get_connection():
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        port=DB_PORT,
    )
    if connection.is_connected():
        print("Connected to MySQL Server")
    return connection


def fetch_users(connection: MySQLConnectionAbstract):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_tb")
    users = cursor.fetchall()
    cursor.close()
    return users


def is_expired(expiry_time: datetime) -> bool:
    if not expiry_time:
        return True
    expiry_time = expiry_time.replace(tzinfo=timezone.utc)
    utc_current_time = datetime.now(timezone.utc)
    return utc_current_time >= expiry_time


def refresh_access_token(connection: MySQLConnectionAbstract, user_id: int, refresh_token: str) -> Credentials:
    credentials = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=SCOPES,
    )
    credentials.refresh(Request())

    cursor = connection.cursor()
    query = "UPDATE user_tb SET access_token = %s, expiry = %s WHERE id = %s"
    cursor.execute(query, (credentials.token, credentials.expiry, user_id))
    connection.commit()
    cursor.close()

    return credentials


def authenticate_gmail(connection: MySQLConnectionAbstract, user: dict):
    refresh_token = user["refresh_token"]

    if is_expired(user["expiry"]):
        print(f"🔄 사용자 {user['id']} 토큰 만료. 새로 갱신 중...")
        creds = refresh_access_token(connection, user["id"], refresh_token)
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


def insert_report(connection: MySQLConnectionAbstract, user_id, report):
    cursor = connection.cursor()
    current_datetime = datetime.now()

    sql = "INSERT INTO report_temp_tb (user_id, content, date, refresh_time) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (user_id, report, current_datetime.date(), current_datetime))
    connection.commit()
    cursor.close()

    print("새로운 레포트가 등록되었습니다.")
