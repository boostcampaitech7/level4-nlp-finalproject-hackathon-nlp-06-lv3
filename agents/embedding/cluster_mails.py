from agents import EmbeddingManager
from batch_serving import Mail


def cluster_mails(mail_dict: dict[str, Mail], config: dict):
    embedding_manager = EmbeddingManager(
        embedding_model_name=config["embedding"]["model_name"],
        similarity_metric=config["embedding"]["similarity_metric"],
        similarity_threshold=config["embedding"]["similarity_threshold"],
        is_save_results=config["embedding"]["save_results"],
    )
    embedding_manager.run(mail_dict)
