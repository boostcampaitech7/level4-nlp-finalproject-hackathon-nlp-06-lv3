import base64
import os
import re

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


def save_file(file_data: str, file_name: str = "attachment", save_dir: str = "downloaded_files") -> None:
    """
    파일 데이터를 정해진 경로에 저장합니다.

    인자:
        file_data (str): 문자열로 인코딩된 파일 정보.
        file_path (str): 파일을 저장할 경로.
    반환값:
        file_path (str): 파일을 저장한 경로.
    """
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, file_name)
    with open(file_path, "wb") as file:
        file.write(file_data)

    return file_path


def replace_match(match):
    """
    정규 표현식으로 매칭된 파일명을 파싱된 파일 내용으로로 대체합니다.

    인자자:
        match (re.Match): 정규 표현식으로 매칭된 객체.
    반환값:
        str: 파일의 내용을 반환하거나, 파일을 찾을 수 없거나 읽기 오류가
            발생한 경우 적절한 오류 메시지를 반환합니다.
    """
    file_name = match.group(1)
    file_path = os.path.join("downloaded_files", file_name)
    try:
        return parse_document(file_path)
    except FileNotFoundError:
        return f"[파일 '{file_name}'을(를) 찾을 수 없음]"
    except Exception as e:
        return f"[파일 읽기 에러: {str(e)}]"


def replace_image_from(plain_text: str):
    """
    주어진 텍스트에서 "[image: 파일명]" 형태로 작성된 패턴을 찾아
    해당 파일의 파싱 결과로 대체합니다.

    인자자:
        plain_text (str): "[image: 파일명]" 패턴을 대체할 원문.
    반환값:
        str: "[image: 파일명]" 패턴이 대체된 수정문.
    """
    pattern = r"\[image: (.+?)\]"
    return re.sub(pattern, replace_match, plain_text)
