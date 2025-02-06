import json

import yaml

from utils.utils import map_category


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


def build_markdown_result(start_time: float, mail_dict) -> str:
    """
    동일한 인자값을 받아서, 기존 콘솔 출력 형태를
    Markdown 형식으로 구성한 문자열을 반환합니다.
    """
    lines = []

    # 헤더
    lines.append("## FINAL_REPORT  \n")  # (줄바꿈+공백은 Markdown 스타일
    #  로 원하는 대로 조정 가능합니다.)

    # 각 메일 정보
    for mail_id, mail in mail_dict.items():
        # 유사 메일 문자열 구성
        # (mail.similar_mails가 있다고 가정)
        sim_mails_str = (
            "\n".join(
                [
                    f"\t{i + 1}번째 유사 메일\n"
                    f"\tID: {sim_mail_id}\n"
                    f"\t제목: {mail_dict[sim_mail_id].subject}\n"
                    f"\t요약: {mail_dict[sim_mail_id].summary}\n"
                    for i, sim_mail_id in enumerate(mail.similar_mails)
                ]
            )
            if hasattr(mail, "similar_mails")
            else ""
        )

        # Mail 정보 출력 부분
        lines.append(f"**ID**: {mail_id}")
        lines.append(f"- 분류: {getattr(mail, 'label_action', '(no label)')}")
        lines.append(f"- 제목: {mail.subject}")
        lines.append(f"- 요약: {mail.summary}")
        if sim_mails_str:
            lines.append("```")
            lines.append(sim_mails_str)
            lines.append("```")
        lines.append(f"{'=' * 40}\n")

    # 최종적으로 줄들을 합쳐 하나의 문자열로 반환
    return "\n".join(lines)
