from agents.pipeline import pipeline
from batch_serving import GmailService, authenticate_gmail, fetch_users, insert_report


def main():
    # 유저 테이블 불러오기
    users = fetch_users()

    # access token, refresh token 가져와서 service 객체 선언하기
    for user in users:
        # try:
        if user["id"] == 9:
            service = authenticate_gmail(user)
            # GmailService 인스턴스 생성
            gmail_service = GmailService(service)

            json_checklist, report = pipeline(gmail_service, user["upstage_api_key"])
            print(f"============ FINAL REPORT of {user['id']} =============")
            print(report)
            print("=======================================================")

            insert_report(user["id"], report, json_checklist)

        # except Exception as e:
        #     print(e)


if __name__ == "__main__":
    main()
