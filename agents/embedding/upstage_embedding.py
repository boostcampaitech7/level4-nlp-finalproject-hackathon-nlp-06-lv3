import os

import numpy as np
from openai import OpenAI

from agents import BaseAgent

from .sentence_splitter import split_sentences


class UpstageEmbeddingAgent(BaseAgent):
    def __init__(self, model: str | None = None, temperature: int | None = None, seed: int | None = None):
        super().__init__(model, temperature, seed=seed)

    def initialize_chat(self, model, temperature=None, seed=None):
        return OpenAI(api_key=os.getenv("UPSTAGE_API_KEY"), base_url="https://api.upstage.ai/v1/solar")

    def process(self, summary: str, model=None) -> np.ndarray:
        splitted_sentences = split_sentences(summary)

        embedding_vectors = []
        if len(splitted_sentences) == 1:
            response = (
                self.client.embeddings.create(input=splitted_sentences[0], model="embedding-query").data[0].embedding
            )
            embedding_vectors.append(response)  # shape == (1, N)
        else:
            response = self.client.embeddings.create(input=splitted_sentences, model="embedding-passage").data
            embedding_vectors = [i.embedding for i in response]  # shape == (k, N)

        embedding_matrix = np.array(embedding_vectors)
        mean_pooled_vector = np.mean(embedding_matrix, axis=0)

        return mean_pooled_vector
