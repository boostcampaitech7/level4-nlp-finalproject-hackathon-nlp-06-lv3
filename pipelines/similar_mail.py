from collections import defaultdict

from agents.embedding.embedding_manager import EmbeddingManager, SimilarityDict
from gmail_api.mail import Mail
from utils.configuration import Config


def group_by_category(mail_dict: dict[str, Mail], categories: dict[int, str]) -> dict[str, dict[str, Mail]]:
    grouped_mail_dict: dict[str, dict[str, Mail]] = defaultdict(dict)
    for mail_id, mail in mail_dict.items():
        grouped_mail_dict[categories[mail_id]][mail_id] = mail
    return grouped_mail_dict


def get_similar_mail_dict(mail_dict: dict[str, Mail]) -> dict[str, list[str]]:
    return EmbeddingManager(
        Config.config["embedding"]["model_name"],
        Config.config["embedding"]["similarity_metric"],
        Config.config["embedding"]["similarity_threshold"],
    ).run(mail_dict)


def save_results(category: str, mail_dict: dict[str, Mail], similar_dict: SimilarityDict):
    if not Config.config["embedding"]["save_results"]:
        return
    _save_top_match(category, mail_dict, similar_dict)
    _save_similar_emails(category, mail_dict, similar_dict)


# built-in functions
def _save_top_match(category: str, mail_dict: dict[str, Mail], similar_dict: SimilarityDict):
    filename = f"{Config.config['embedding']['model_name']}_{category}_top_match.txt"

    with open(filename, "w", encoding="utf-8") as f:
        for mail_id, similar_list in similar_dict.items():
            f.write(f"Email ID: {mail_id}\n")
            f.write(f"Data: {mail_dict[mail_id].subject}\n")
            f.write("Similar Emails:\n")
            if similar_list:
                top_match_id, top_match_score = similar_list[0]
                f.write(f"  - Top Match: {top_match_id} (Score: {top_match_score:.4f})\n")
                f.write(f"    Top Match Data: {mail_dict[top_match_id].subject}\n")
            else:
                f.write("  - No similar emails found.\n")
            f.write("\n" + "=" * 80 + "\n\n")
    print(f"Saved similar emails to {filename}")


def _save_similar_emails(category: str, mail_dict: dict[str, Mail], similar_dict: SimilarityDict):
    filename = (
        f"{Config.config['embedding']['model_name']}_{category}"
        "_{Config.config['embedding']['similarity_metric']}_similarities.txt"
    )

    txt_content = "\n\n".join(
        f"Email ID: {mail_id}\nData: {mail_dict[mail_id].subject}\nSimilar Emails:\n"
        + "\n".join(f"  - {sim_id}: {sim_score:.4f}" for sim_id, sim_score in similar_dict[mail_id])
        for mail_id in similar_dict.keys()
    )
    with open(filename, "w", encoding="utf-8") as f:
        f.write(txt_content)
    print(f"Saved similar emails to {filename}")
