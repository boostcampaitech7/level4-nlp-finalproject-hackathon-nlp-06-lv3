from collections import defaultdict

from agents.embedding.embedding_manager import EmbeddingManager
from gmail_api.mail import Mail
from utils.configuration import Config


def cluster_mails(mail_dict: dict[str, Mail], categories: dict[int, str]) -> dict[str, list[str]]:
    # TODO: 분류 기준 추가 시 데이터 파싱 변경
    grouped_dict: dict[str, dict[str, Mail]] = defaultdict(dict)
    for mail_id, mail in mail_dict.items():
        grouped_dict[categories[mail_id]][mail_id] = mail

    return EmbeddingManager(
        embedding_model_name=Config.config["embedding"]["model_name"],
        similarity_metric=Config.config["embedding"]["similarity_metric"],
        similarity_threshold=Config.config["embedding"]["similarity_threshold"],
        is_save_results=Config.config["embedding"]["save_results"],
    ).run(grouped_dict)
