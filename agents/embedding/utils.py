import numpy as np

from gmail_api.mail import Mail


def compute_similarity(embedding_vectors: dict[str, np.ndarray]) -> dict[str, tuple[str, float]]:
    mail_ids = list(embedding_vectors.keys())
    embedding_matrix = np.array(list(embedding_vectors.values()))
    similarity_matrix = np.dot(embedding_matrix, embedding_matrix.T)

    similar_results: dict[str, tuple[str, float]] = {
        mail_ids[i]: [
            (mail_ids[j], float(similarity_matrix[i][j])) for j in np.argsort(-similarity_matrix[i]) if j != i
        ]
        for i in range(len(mail_ids))
    }

    return similar_results


def save_email_similarity_results(
    mail_dict: dict[str, Mail], similar_results: dict[str, tuple[str, float]], filename="top_match.txt"
):
    with open(filename, "w", encoding="utf-8") as f:
        for mail_id, similar_list in similar_results.items():
            f.write(f"Email ID: {mail_id}\n")
            f.write(f"Summary: {mail_dict[mail_id].summary}\n")
            f.write("Similar Emails:\n")
            if similar_list:
                top_match_id, top_match_score = similar_list[0]
                f.write(f"  - Top Match: {top_match_id} (Score: {top_match_score:.4f})\n")
                f.write(f"    Top Match Summary: {mail_dict[top_match_id].summary}\n")
            else:
                f.write("  - No similar emails found.\n")
            f.write("\n" + "=" * 80 + "\n\n")
    print(f"Saved similar emails to {filename}")


def save_similar_emails(
    mail_dict: dict[str, Mail], similar_results: dict[str, tuple[str, float]], filename="dot_product_similarities.txt"
):
    txt_content = "\n\n".join(
        f"Email ID: {mail_id}\nSummary: {mail_dict[mail_id].summary}\nSimilar Emails:\n"
        + "\n".join(f"  - {sim_id}: {sim_score:.4f}" for sim_id, sim_score in similar_results[mail_id])
        for mail_id in similar_results.keys()
    )
    with open(filename, "w", encoding="utf-8") as f:
        f.write(txt_content)
    print(f"Saved similar emails to {filename}")
