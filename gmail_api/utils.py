import base64
import logging
import os
import re
from collections import deque
from typing import Optional

import requests
from langchain_upstage import UpstageDocumentParseLoader

logging.basicConfig(level=logging.WARNING, filename="gmail_api/gmail_error.log")


def is_supported_format(file_path: str) -> bool:
    supported_formats = ["jpeg", "png", "bmp", "pdf", "tiff", "heic", "docx", "pptx", "xlsx"]
    file_name = os.path.basename(file_path)
    file_extension = os.path.splitext(file_name)[1][1:].lower()
    return file_extension in supported_formats


def parse_document(file_path) -> str:
    if is_supported_format(file_path):
        loader = UpstageDocumentParseLoader(file_path)
        pages = loader.load()

        parsed_document = ""
        for page in pages:
            parsed_document += page.page_content
        return parsed_document
    else:
        # 지원되지 않는 형식일 경우 파일명만 반환
        return f"{os.path.basename(file_path)}"


def decode_base64(data: str) -> bytes:
    data = data.replace("-", "+").replace("_", "/")
    return base64.b64decode(data)


def save_file(file_data: bytes, file_name: str, save_dir: str = "downloaded_files") -> Optional[str]:
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


def replace_pattern_with(parsed_items: dict, text: str, pattern: str) -> str:
    def replacement(match):
        key = match.group(1)
        return parsed_items.get(key, match.group(0))  # 매칭된 키가 없으면 원본 유지

    return re.sub(pattern, replacement, text)


def remove_http_brackets(text):
    return re.sub(r"<[^>]*http[^>]*>", "", text)


def replace_url_pattern_from(plain_text: str) -> str:

    clean_text = remove_http_brackets(plain_text)
    url_pattern = r"\[([^\]]+)\]"
    urls = re.findall(url_pattern, clean_text)
    url_to_parsed_image = {}

    for url in urls:
        try:
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
            clean_text.replace("url", "")
        except Exception as e:
            logging.warning(f"Failed to process {url}: {e}")

    return replace_pattern_with(url_to_parsed_image, clean_text, url_pattern)


def replace_image_pattern_with(plain_text: str, files: deque):
    def replacement(match):
        return files.popleft() if files else match.group(0)

    updated_text = re.sub(r"\[image: (.+?)\]", replacement, plain_text)
    return updated_text, files
