import logging
from abc import ABC, abstractmethod
from collections import Counter

import httpx

from app.core.config import settings

logger = logging.getLogger("sedap.embeddings")

OPENAI_EMBEDDINGS_URL = "https://api.openai.com/v1/embeddings"
_STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "is",
    "are", "was", "were", "at", "by", "as", "it", "this", "that", "from", "be",
}


class EmbeddingService(ABC):
    dimension: int

    @abstractmethod
    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        ...


class LocalEmbeddingProvider(EmbeddingService):
    def __init__(self, dimension: int | None = None) -> None:
        self.dimension = dimension or settings.EMBEDDING_DIMENSION

    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def _embed(self, text: str) -> list[float]:
        tokens = [
            t for t in text.lower().split()
            if t.isalpha() and t not in _STOPWORDS
        ]
        counts = Counter(tokens)
        vec = [0.0] * self.dimension
        if counts:
            for term, freq in counts.items():
                idx = (hash(term) % self.dimension + self.dimension) % self.dimension
                vec[idx] += float(freq)
        norm = sum(v * v for v in vec) ** 0.5
        if norm == 0.0:
            return vec
        return [v / norm for v in vec]


class OpenAIEmbeddingProvider(EmbeddingService):
    def __init__(self, model: str | None = None, dimension: int | None = None) -> None:
        self.model = model or settings.EMBEDDING_MODEL
        self.dimension = dimension or settings.EMBEDDING_DIMENSION
        if not settings.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is required when EMBEDDING_PROVIDER=openai"
            )

    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {"model": self.model, "input": texts}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(OPENAI_EMBEDDINGS_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        vectors = [item["embedding"] for item in data["data"]]
        if len(vectors) != len(texts):
            raise ValueError("OpenAI embedding count mismatch")
        return vectors


def get_embedding_service() -> EmbeddingService:
    provider = settings.EMBEDDING_PROVIDER
    if provider == "local":
        return LocalEmbeddingProvider()
    if provider == "openai":
        return OpenAIEmbeddingProvider()
    raise ValueError(f"Unsupported EMBEDDING_PROVIDER: {provider!r} (supported: 'local', 'openai')")
