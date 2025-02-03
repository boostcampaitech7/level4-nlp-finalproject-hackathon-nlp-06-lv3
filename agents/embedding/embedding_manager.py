from typing import Callable, TypedDict

import numpy as np

from gmail_api import Mail
from utils.utils import group_mail_dict_2_classification

from .bge_m3_embedding import Bgem3EmbeddingAgent
from .upstage_embedding import UpstageEmbeddingAgent


class SimilarityEntry(TypedDict):
    mail_id: str
    similarity_score: float


class SimilarityDict(TypedDict):
    """
    {
        메일 ID: [
            (Top 1 메일 ID, 유사도),
            ...
        ],
        ...
    }
    """

    mail_id: list[SimilarityEntry]


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
    similar_results = {
        mail_ids[i]: [
            (mail_ids[j], float(similarity_matrix[i][j])) for j in np.argsort(-similarity_matrix[i]) if j != i
        ]
        for i in range(len(mail_ids))
    }

    return similar_results


def _compute_cosine_similarity(embedding_vectors: dict[str, np.ndarray]) -> SimilarityDict:
    # TODO: 코사인 유사도 구현
    pass


class EmbeddingManager:
    def __init__(
        self,
        embedding_model_name: str,
        similarity_metric: str,
        similarity_threshold: int = None,
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
        elif similarity_metric == "cosine_similarity":
            self.compute_similarity: Callable[[dict[str, np.ndarray]], SimilarityDict] = _compute_cosine_similarity
        else:
            raise ValueError(f"{similarity_metric}은 유효한 유사도 메트릭이 아닙니다.")

        self.threshold = similarity_threshold
        self.is_save_results = is_save_results

    def run(self, mail_dict: dict[str, Mail]):
        grouped_dict = group_mail_dict_2_classification(mail_dict)

        for category, grouped_mail_dict in grouped_dict.items():
            embedding_vectors = {
                mail_id: self.embedding_model.process(mail.summary) for mail_id, mail in grouped_mail_dict.items()
            }
            similarities = self.compute_similarity(embedding_vectors)

            if self.is_save_results:
                self._save_top_match(category, grouped_mail_dict, similarities)
                self._save_similar_emails(category, grouped_mail_dict, similarities)

            # TODO: Threshold 값 적용 후 반환하기

    # built-in functions

    def _save_top_match(self, category: str, mail_dict: dict[str, Mail], similar_results: SimilarityDict):
        filename = f"{self.model_name}_{category}_top_match.txt"

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

    def _save_similar_emails(self, category: str, mail_dict: dict[str, Mail], similar_results: SimilarityDict):
        filename = f"{self.model_name}_{category}_{self.compute_similarity.__name__}_similarities.txt"

        txt_content = "\n\n".join(
            f"Email ID: {mail_id}\nSummary: {mail_dict[mail_id].summary}\nSimilar Emails:\n"
            + "\n".join(f"  - {sim_id}: {sim_score:.4f}" for sim_id, sim_score in similar_results[mail_id])
            for mail_id in similar_results.keys()
        )
        with open(filename, "w", encoding="utf-8") as f:
            f.write(txt_content)
        print(f"Saved similar emails to {filename}")
