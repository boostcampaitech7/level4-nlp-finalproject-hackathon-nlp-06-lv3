from dotenv import load_dotenv
from langchain_upstage import UpstageDocumentParseLoader


def parse_document(file_path) -> str:
    load_dotenv()
    loader = UpstageDocumentParseLoader(file_path)
    pages = loader.load()

    parsed_document = ""
    for page in pages:
        parsed_document += page.page_content

    return parsed_document


if __name__ == "__main__":
    file_path = "downloaded_files/image.png"
    print(parse_document(file_path))
