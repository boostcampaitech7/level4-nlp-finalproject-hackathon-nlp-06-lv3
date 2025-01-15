import dotenv

from summary import total_report


def main():
    # 초기 환경 설정
    dotenv.load_dotenv()

    # 개별 메일 요약 -> 요약된 개별 메일로 이루어진 리스트
    with (
        open("samples/mail1.txt", "r", encoding="utf-8") as file1,
        open("samples/mail2.txt", "r", encoding="utf-8") as file2,
    ):
        individual_summaries = [file1.read(), file2.read()]

    # 메일 정리 -> 텍스트
    result = total_report(individual_summaries, debug=True)

    # 어딘가로 전송
    print(result)


if __name__ == "__main__":
    main()
