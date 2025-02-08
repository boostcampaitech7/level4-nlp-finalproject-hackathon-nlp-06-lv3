import numpy as np
from sentence_transformers import SentenceTransformer

from agents import BaseAgent
from utils.utils import retry_with_exponential_backoff

from .sentence_splitter import split_sentences


class Bgem3EmbeddingAgent(BaseAgent):
    def __init__(
        self, model_name: str = "upskyy/bge-m3-korean", temperature: int | None = None, seed: int | None = None
    ):
        super().__init__(model_name, temperature, seed)

    def initialize_chat(self):
        return SentenceTransformer(self.model_name)

    @retry_with_exponential_backoff()
    def process(self, summary: str, model=None):
        splitted_sentences = split_sentences(summary)

        embedding_vectors = self.client.encode(splitted_sentences)

        embedding_matrix = np.array(embedding_vectors)
        mean_pooled_vector = np.mean(embedding_matrix, axis=0)

        return mean_pooled_vector
