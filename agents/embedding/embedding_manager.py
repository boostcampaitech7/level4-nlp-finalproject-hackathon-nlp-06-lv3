from typing import Callable, TypedDict

import numpy as np

from agents.embedding.bge_m3_embedding import Bgem3EmbeddingAgent
from agents.embedding.upstage_embedding import UpstageEmbeddingAgent
from gmail_api.mail import Mail


class SimilarityDict(TypedDict):
    class SimilarityEntry(TypedDict):
        mail_id: str
        similarity_score: float

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

    def run(self, mail_dict: dict[str, Mail]) -> list[str]:
        embedding_vectors = {mail_id: self.embedding_model.process(mail.subject) for mail_id, mail in mail_dict.items()}
        similar_dict = self.compute_similarity(embedding_vectors)

        # TODO: prefix를 붙여서 2가지 분류 기준을 구분할 것
        return self._process_similar_mails(similar_dict)

    def _process_similar_mails(self, similar_dict: SimilarityDict) -> dict[str, list[str]]:
        filtered_dict: dict[str, list[str]] = {
            mail_id: [sim_id for sim_id, sim_score in similar_list if sim_score >= self.threshold]
            for mail_id, similar_list in similar_dict.items()
        }
        return filtered_dict
