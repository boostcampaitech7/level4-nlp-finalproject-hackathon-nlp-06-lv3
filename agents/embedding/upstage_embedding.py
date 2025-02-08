import os

import numpy as np
from openai import OpenAI

from agents.base_agent import BaseAgent
from agents.embedding.sentence_splitter import split_sentences


class UpstageEmbeddingAgent(BaseAgent):
    def __init__(self, model_name: str | None = None, temperature: int | None = None, seed: int | None = None):
        super().__init__(model_name, temperature, seed)

    def initialize_chat(self):
        return OpenAI(
            api_key=os.getenv("UPSTAGE_API_KEY"), base_url="https://api.upstage.ai/v1/solar"
        )  # TODO: 유저 별로 UPSTAGE_API_KEY 사용하게 변경

    def process(self, summary: str, model=None) -> np.ndarray:
        splitted_sentences = split_sentences(summary)

        response = self.client.embeddings.create(input=splitted_sentences, model="embedding-passage").data
        embedding_vectors = [i.embedding for i in response]  # shape == (k, N)

        embedding_matrix = np.array(embedding_vectors)
        mean_pooled_vector = np.mean(embedding_matrix, axis=0)

        return mean_pooled_vector
