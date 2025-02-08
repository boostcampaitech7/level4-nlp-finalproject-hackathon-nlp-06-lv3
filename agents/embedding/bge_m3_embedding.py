import numpy as np
from sentence_transformers import SentenceTransformer

from agents.embedding.sentence_splitter import split_sentences
from utils.utils import retry_with_exponential_backoff


class Bgem3EmbeddingAgent:
    def __init__(self, model_name: str = "upskyy/bge-m3-korean"):
        self.model = SentenceTransformer(model_name)

    @retry_with_exponential_backoff()
    def process(self, summary: str):
        splitted_sentences = split_sentences(summary)

        embedding_vectors = self.model.encode(splitted_sentences)

        embedding_matrix = np.array(embedding_vectors)
        mean_pooled_vector = np.mean(embedding_matrix, axis=0)

        return mean_pooled_vector
