import numpy as np
from openai import OpenAI

from agents.embedding.sentence_splitter import split_sentences
from utils.configuration import Config


class UpstageEmbeddingAgent:
    def __init__(self):
        self.client = OpenAI(api_key=Config.user_upstage_api_key, base_url="https://api.upstage.ai/v1/solar")

    def process(self, summary: str, model=None) -> np.ndarray:
        splitted_sentences = split_sentences(summary)

        response = self.client.embeddings.create(input=splitted_sentences, model="embedding-passage").data
        embedding_vectors = [i.embedding for i in response]  # shape == (k, N)

        embedding_matrix = np.array(embedding_vectors)
        mean_pooled_vector = np.mean(embedding_matrix, axis=0)

        return mean_pooled_vector
