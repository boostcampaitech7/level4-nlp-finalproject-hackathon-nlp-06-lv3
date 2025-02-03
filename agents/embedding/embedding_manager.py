from typing import Callable, TypedDict

import numpy as np

from gmail_api import Mail

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
    pass


class EmbeddingManager:
    def __init__(self, embedding_model_name: str, similarity_metric: str, save_similarity_results: bool = False):
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

        self.save_similarity_results = save_similarity_results

    def run(self, mail_dict: dict[str, Mail]):
        embedding_vectors = {mail_id: self.embedding_model.process(mail.summary) for mail_id, mail in mail_dict.items()}
        similarities = self.compute_similarity(embedding_vectors)
        print(similarities)
