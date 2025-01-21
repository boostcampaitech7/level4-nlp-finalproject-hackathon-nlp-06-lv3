import base64
import os
import re
from collections import deque


def decode_base64(data: str) -> bytes:
    """
    base64로 인코딩된 메시지 부분을 디코딩합니다.

    인자:
        data (str): base64로 인코딩된 문자열.
    반환값:
        bytes: 디코드 결과 바이트 스트림.
    """
    data = data.replace("-", "+").replace("_", "/")
    return base64.b64decode(data)


def save_file(file_data: str, file_name: str = "attachment", save_dir: str = "downloaded_files") -> None:
    """
    파일 데이터를 정해진 경로에 저장합니다.

    인자:
        file_data (str): 저장할 파일 정보.
        file_path (str): 저장할 파일 이름름.
    반환값:
        file_path (str): 파일을 저장한 경로.
    """
    try:
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, file_name)
        with open(file_path, "wb") as file:
            file.write(file_data)
        return file_path
    except Exception as e:
        print(f"An error occurred while saving the file: {e}")
        return None


def delete_file(saved_file_path: str) -> bool:
    """
    파일 경로에 저장된 데이터를 삭제합니다.

    인자:
        saved_file_path (str): 삭제할 파일의 경로.
    반환값:
        bool: 파일 삭제 성공 여부.
    """
    try:
        if os.path.exists(saved_file_path):
            os.remove(saved_file_path)
            return True
        else:
            print(f"The file does not exist: {saved_file_path}")
            return False
    except Exception as e:
        print(f"An error occurred while deleting the file: {e}")
        return False


def replace_image_patten_with(plain_text: str, files: deque) -> str:
    """
    `plain_text` 내 `[image: ]` 패턴을 찾아 `files` 리스트의 leftpop 값으로 대체합니다.

    인자:
        plain_text (str): 대체가 필요한 텍스트.
        files (deque): 대체할 파일 내용을 포함한 deque.
    반환값:
        updated_text (str): 대체가 완료된 텍스트.
        files (deque): 대체된 뒤 남은 파일 내용을 포함한 deque.
    """
    matches = list(re.finditer(r"\[image: (.+?)\]", plain_text))

    if not matches:
        return plain_text, files

    def replacement(match):
        # files에서 첫번째 요소를 반환하거나, files가 비어있을 경우 원문을 그대로 반환한다.
        return files.popleft() if files else match.group(0)

    updated_text = re.sub(r"\[image: (.+?)\]", replacement, plain_text)

    return updated_text, files
