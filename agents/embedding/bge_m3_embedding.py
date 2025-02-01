from sentence_transformers import SentenceTransformer

from agents import BaseAgent


class Bgem3EmbeddingAgent(BaseAgent):
    def __init__(self, model: str | None = None, temperature: int | None = None, seed: int | None = None):
        super().__init__(model, temperature, seed=seed)

    def initialize_chat(self, model, temperature=None, seed=None):
        return SentenceTransformer("upskyy/bge-m3-korean")

    def process(self, data: list[str], model=None):
        return super().process(data, model)
