import os

from langchain_upstage import UpstageDocumentParseLoader


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
        return f"{os.path.basename(file_path)}"
