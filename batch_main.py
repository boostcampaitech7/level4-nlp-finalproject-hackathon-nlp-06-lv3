from dotenv import load_dotenv

from batch_serving.db_utils import authenticate_gmail, fetch_users, insert_report
from gmail_api.gmail_service import GmailService
from pipelines.pipeline import pipeline
from utils.configuration import Config


def main():
    load_dotenv()
    Config.load()

    # 유저 테이블 불러오기
    users = fetch_users()

    # access token, refresh token 가져와서 service 객체 선언하기
    for user in users:
        try:
            if user["id"] != 9:
                continue

            service = authenticate_gmail(user)
            Config.user_upstage_api_key = user["upstage_api_key"]
            # GmailService 인스턴스 생성
            gmail_service = GmailService(service)

            json_checklist, report = pipeline(gmail_service)
            print(f"============ FINAL REPORT of {user['id']} =============")
            print(report)
            print("=======================================================")

            insert_report(user["id"], report, json_checklist)

        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
