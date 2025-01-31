import yaml
import json


def load_config(config_path):
    """
    주어진 경로의 YAML 설정 파일을 로드하여 dict 형태로 반환
    """
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_report_data(json_file):
    """
    JSON을 로드하여 source, report, reference 리스트를 반환
    """
    with open(json_file, "r", encoding="utf-8") as f:
        data_list = json.load(f)

    source_texts, report_texts, reference_texts = [], [], []

    for item in data_list:
        source_texts.append(item["source"])
        report_texts.append(item["report"])
        reference_texts.append(item.get("reference", None))  # gold summary 없을 경우 None

    return source_texts, report_texts, reference_texts
