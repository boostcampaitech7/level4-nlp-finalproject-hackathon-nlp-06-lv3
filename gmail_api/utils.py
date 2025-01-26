import base64
import os
import re
from collections import deque
from typing import Optional

import requests

from .document_parse import parse_document


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


def save_file(file_data: bytes, file_name: str, save_dir: str = "downloaded_files") -> Optional[str]:
    """
    파일 데이터를 정해진 경로에 저장합니다.

    인자:
        file_data (str): 저장할 파일 정보.
        file_path (str): 저장할 파일 이름.
    반환값:
        Optional[str]: 파일을 저장 성공시 저장 경로, 실패 시 None.
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


def replace_image_pattern_with(plain_text: str, files: deque) -> str:
    """
    `[image: ]` 패턴을 deque에서 가져온 값으로 대체합니다.

    Args:
        plain_text (str): 패턴을 대체할 텍스트.
        files (deque): 대체할 파일 내용이 저장된 deque.

    Returns:
        str: 패턴이 대체된 텍스트.
    """

    def replacement(match):
        # files에서 첫 번째 요소를 반환하거나, files가 비어있을 경우 원문을 그대로 반환
        return files.popleft() if files else match.group(0)

    updated_text = re.sub(r"\[image: (.+?)\]", replacement, plain_text)
    return updated_text, files


def replace_pattern_with(parsed_items: dict, text: str, pattern: str) -> str:
    """
    텍스트에서 주어진 패턴을 찾아, 매칭된 항목을 파싱된 값으로 대체합니다.

    인자:
        parsed_items (dict): 패턴 매칭값과 대체값의 매핑 딕셔너리.
        text (str): 패턴을 대체할 텍스트.
        pattern (str): 대체할 패턴.

    반환값:
        str: 대체가 완료된 텍스트.
    """

    def replacement(match):
        key = match.group(1)
        return parsed_items.get(key, match.group(0))  # 매칭된 키가 없으면 원본 유지

    return re.sub(pattern, replacement, text)


def replace_url_pattern_from(plain_text):
    """
    텍스트에서 URL 패턴을 추출하고 이미지를 다운로드하여 저장한 뒤,
    URL 패턴을 대체된 값으로 업데이트합니다.

    인자:
        plain_text (str): URL을 포함한 텍스트.
        save_dir (str): 이미지를 저장할 디렉토리 경로.
    반환값:
        str: URL 패턴이 대체된 텍스트.
    """
    url_pattern = r"\[([^\]]+)\]"
    urls = re.findall(url_pattern, plain_text)
    url_to_parsed_image = {}

    for url in urls:
        try:
            # URL에 요청을 보내 해당 content의 타입을 확인
            response = requests.get(url, stream=True, timeout=10)
            content_type = response.headers.get("Content-Type", "")

            if "image" in content_type:
                file_extension = content_type.split("/")[-1].split(";")[0]
                file_name = url.split("/")[-1].split("?")[0]

                if not file_name.endswith(file_extension):
                    file_name += f".{file_extension}"

                file_data = response.content
                file_path = save_file(file_data, file_name)

                if file_path:
                    parsed_image = parse_document(file_path)
                    url_to_parsed_image[url] = parsed_image
                    delete_file(file_path)
            else:
                print(f"URL is not an image: {url}")
        except Exception as e:
            print(f"Failed to process {url}: {e}")

    return replace_pattern_with(url_to_parsed_image, plain_text, url_pattern)
