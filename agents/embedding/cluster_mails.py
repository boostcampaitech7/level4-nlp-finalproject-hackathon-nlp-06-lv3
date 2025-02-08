from agents import EmbeddingManager
from gmail_api.mail import Mail
from utils.configuration import Config


def cluster_mails(mail_dict: dict[str, Mail]):
    embedding_manager = EmbeddingManager(
        embedding_model_name=Config.config["embedding"]["model_name"],
        similarity_metric=Config.config["embedding"]["similarity_metric"],
        similarity_threshold=Config.config["embedding"]["similarity_threshold"],
        is_save_results=Config.config["embedding"]["save_results"],
    )
    embedding_manager.run(mail_dict)
