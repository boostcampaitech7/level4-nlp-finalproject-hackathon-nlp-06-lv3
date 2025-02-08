from typing import Callable

import numpy as np

from agents.embedding.bge_m3_embedding import Bgem3EmbeddingAgent
from agents.embedding.typing import SimilarityDict
from agents.embedding.upstage_embedding import UpstageEmbeddingAgent
from gmail_api.mail import Mail
from utils.utils import group_mail_dict_2_classification


def _compute_dot_product_similarity(embedding_vectors: dict[str, np.ndarray]) -> SimilarityDict:
    mail_ids = list(embedding_vectors.keys())
    embedding_matrix = np.array(list(embedding_vectors.values()))
    similarity_matrix = np.dot(embedding_matrix, embedding_matrix.T)

    # {
    #   "mail_id_1": [
    #       ("top_1_mail_id", 0.xxx),
    #       ("top_2_mail_id", 0.xxx)
    #   ],
    #   "mail_id_2": [],
    #   ...
    # }
    similar_results: SimilarityDict = {
        mail_ids[i]: [
            (mail_ids[j], float(similarity_matrix[i][j])) for j in np.argsort(-similarity_matrix[i]) if j != i
        ]
        for i in range(len(mail_ids))
    }

    return similar_results


def _compute_cosine_similarity(embedding_vectors: dict[str, np.ndarray]) -> SimilarityDict:
    mail_ids = list(embedding_vectors.keys())
    embedding_matrix = np.array(list(embedding_vectors.values()))

    # 코사인 유사도 행렬 계산
    norm_matrix = np.linalg.norm(embedding_matrix, axis=1, keepdims=True)
    normalized_embeddings = embedding_matrix / (norm_matrix + 1e-10)  # 0으로 나누는 것 방지
    similarity_matrix = np.dot(normalized_embeddings, normalized_embeddings.T)

    similar_results: SimilarityDict = {
        mail_ids[i]: [
            (mail_ids[j], float(similarity_matrix[i][j])) for j in np.argsort(-similarity_matrix[i]) if j != i
        ]
        for i in range(len(mail_ids))
    }

    return similar_results


class EmbeddingManager:
    def __init__(
        self,
        embedding_model_name: str,
        similarity_metric: str,
        similarity_threshold: float = 0.51,
        is_save_results: bool = False,
    ):
        self.model_name = embedding_model_name

        if embedding_model_name == "bge-m3":
            self.embedding_model = Bgem3EmbeddingAgent()
        elif embedding_model_name == "upstage":
            self.embedding_model = UpstageEmbeddingAgent()
        else:
            raise ValueError(f"{embedding_model_name}은 유효한 임베딩 모델명이 아닙니다.")

        if similarity_metric == "dot-product":
            self.compute_similarity: Callable[[dict[str, np.ndarray]], SimilarityDict] = _compute_dot_product_similarity
        elif similarity_metric == "cosine-similarity":
            self.compute_similarity: Callable[[dict[str, np.ndarray]], SimilarityDict] = _compute_cosine_similarity
        else:
            raise ValueError(f"{similarity_metric}은 유효한 유사도 메트릭이 아닙니다.")

        self.threshold = similarity_threshold
        self.is_save_results = is_save_results

    def run(self, mail_dict: dict[str, Mail]) -> dict[str, Mail]:
        grouped_dict = group_mail_dict_2_classification(mail_dict)

        clustered_dict: dict[str, dict[str, list[str]]] = {}
        for category, grouped_mail_dict in grouped_dict.items():
            embedding_vectors = {
                mail_id: self.embedding_model.process(mail.subject) for mail_id, mail in grouped_mail_dict.items()
            }
            similar_dict = self.compute_similarity(embedding_vectors)

            if self.is_save_results:
                self._save_top_match(category, grouped_mail_dict, similar_dict)
                self._save_similar_emails(category, grouped_mail_dict, similar_dict)

            # TODO: prefix를 붙여서 2가지 분류 기준을 구분할 것
            clustered_dict.update({category: self._process_similar_mails(similar_dict)})

        for similar_mail_dict in clustered_dict.values():
            for mail_id, similar_mail_list in similar_mail_dict.items():
                mail_dict[mail_id].similar_mails = similar_mail_list

    # built-in functions
    def _save_top_match(self, category: str, mail_dict: dict[str, Mail], similar_dict: SimilarityDict):
        filename = f"{self.model_name}_{category}_top_match.txt"

        with open(filename, "w", encoding="utf-8") as f:
            for mail_id, similar_list in similar_dict.items():
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

    def _save_similar_emails(self, category: str, mail_dict: dict[str, Mail], similar_dict: SimilarityDict):
        filename = f"{self.model_name}_{category}_{self.compute_similarity.__name__}_similarities.txt"

        txt_content = "\n\n".join(
            f"Email ID: {mail_id}\nSummary: {mail_dict[mail_id].summary}\nSimilar Emails:\n"
            + "\n".join(f"  - {sim_id}: {sim_score:.4f}" for sim_id, sim_score in similar_dict[mail_id])
            for mail_id in similar_dict.keys()
        )
        with open(filename, "w", encoding="utf-8") as f:
            f.write(txt_content)
        print(f"Saved similar emails to {filename}")

    def _process_similar_mails(self, similar_dict: SimilarityDict) -> dict[str, list[str]]:
        filtered_dict: dict[str, list[str]] = {
            mail_id: [sim_id for sim_id, sim_score in similar_list if sim_score >= self.threshold]
            for mail_id, similar_list in similar_dict.items()
        }
        return filtered_dict
