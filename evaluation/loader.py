import yaml
import json
from agents import map_category


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


def format_source_texts_for_report(source_texts: list) -> str:
    """
    기존 source_texts 리스트를 하나의 plain text로 변환하여 반환하는 함수.

    Args:
        source_texts (list): 개별 이메일 텍스트 리스트.

    Returns:
        str: "<SEP>"로 구분된 단일 plain text.
    """
    return " <SEP> ".join(source_texts)


def generate_final_report_text(report, mail_dict) -> str:
    """
    최종 리포트를 plain text로 생성하여 반환하는 함수.

    Args:
        report (dict): 분류된 메일 및 요약 리포트.
        mail_dict (dict): 메일 ID를 키로 갖는 메일 데이터.

    Returns:
        str: 최종 리포트 plain text
    """
    final_report = "=============FINAL_REPORT================\n"

    for label, mail_reports in report.items():
        category_name = map_category(label)
        final_report += f"{category_name}\n"

        for mail_report in mail_reports:
            mail_subject = mail_dict[mail_report["mail_id"]].subject
            report_text = mail_report["report"]  # 리포트 내용 가져오기

            final_report += f"메일 subject: {mail_subject}\n"
            final_report += f"리포트: {report_text}\n"

        final_report += "\n"  # 카테고리별 줄바꿈 추가

    return final_report
