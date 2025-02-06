from batch_serving import GmailService, authenticate_gmail, fetch_users, get_connection, insert_report
from summary_and_report import summary_and_report


def main():
    # MaeilMail DB 접속
    connection = get_connection()

    # 유저 테이블 불러오기
    users = fetch_users(connection)

    # access token, refresh token 가져와서 service 객체 선언하기
    for user in users:
        user_id = user["id"]
        api_key = user["upstage_api_key"]

        # print(type(api_key))
        try:
            service = authenticate_gmail(connection, user_id)
            # GmailService 인스턴스 생성
            gmail_service = GmailService(service)

            final_report = summary_and_report(gmail_service, api_key)

            insert_report(connection, user["id"], final_report)

        except Exception as e:
            print(e)
            continue

    connection.close()
    print("MySQL connection is closed")


if __name__ == "__main__":
    main()
