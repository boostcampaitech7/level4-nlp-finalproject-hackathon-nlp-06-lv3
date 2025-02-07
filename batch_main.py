from agents.pipeline import pipeline
from batch_serving import GmailService, authenticate_gmail, fetch_users, get_connection, insert_report


def main():
    # MaeilMail DB 접속
    connection = get_connection()

    # 유저 테이블 불러오기
    users = fetch_users(connection)

    # access token, refresh token 가져와서 service 객체 선언하기
    for user in users:
        # try:
        if user["id"] == 9:
            service = authenticate_gmail(connection, user)
            # GmailService 인스턴스 생성
            gmail_service = GmailService(service)

            json_checklist, report = pipeline(gmail_service, user["upstage_api_key"])
            print("=" * 10)
            print("user_id", user["id"])
            print(report)

            insert_report(connection, user["id"], json_checklist)

        # except Exception as e:
        #     print(e)

    connection.close()
    print("MySQL connection is closed")


if __name__ == "__main__":
    main()
