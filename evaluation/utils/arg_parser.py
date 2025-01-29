import argparse


def str2bool(value):
    """문자열 값을 Boolean 값으로 변환하는 함수."""
    if isinstance(value, bool):
        return value
    if value.lower() in ("true", "1", "yes", "y"):
        return True
    elif value.lower() in ("false", "0", "no", "n"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean 값(True/False)을 입력해야 합니다.")


def parse_arguments():
    """명령줄 인자를 파싱하는 함수."""
    parser = argparse.ArgumentParser(description="메일 데이터 분류 및 평가 프로그램")
    parser.add_argument(
        "-he",
        "--human-evaluation",
        type=str2bool,
        nargs="?",
        const=True,
        default=True,
        help="휴먼 평가를 활성화(True) 또는 비활성화(False)할 수 있습니다. 기본값은 True입니다.",
    )
    parser.add_argument(
        "-i", "--inference", nargs="?", const=3, default=3, help="대상 모델의 추론 횟수를 설정합니다. 기본값은 3입니다."
    )
    return parser.parse_args()
