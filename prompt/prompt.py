import os


def load_template(template_type: str, file_name: str) -> str:
    """
    지정된 파일 이름과 템플릿 유형에 따라 템플릿 파일을 로드합니다.

    Args:
        template_type (str):
            템플릿이 위치한 디렉토리 유형을 나타내는 문자열 (예: "summary")
        file_name (str):
            로드할 템플릿 파일의 이름 (예: "single.txt").

    Raises:
        FileNotFoundError:
            지정된 파일이 존재하지 않을 경우 발생.

    Returns:
        str:
            템플릿 파일의 내용을 문자열로 반환.
    """
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, "template", template_type, file_name)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Template file '{file_name}' not found.")

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read().strip()
