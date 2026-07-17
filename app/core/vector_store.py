import logging
import math
from abc import ABC, abstractmethod
from hashlib import sha256

from pydantic import BaseModel, Field

from app.core.config import settings

logger = logging.getLogger("sedap.vector_store")


class VectorRecord(BaseModel):
    id: str
    vector: list[float] = Field(default_factory=list)
    payload: dict[str, object] = Field(default_factory=dict)


class SearchHit(BaseModel):
    id: str
    score: float
    payload: dict[str, object] = Field(default_factory=dict)


class VectorStorageClient(ABC):
    @abstractmethod
    async def upsert_vectors(self, collection_name: str, records: list[VectorRecord]) -> int:
        ...

    @abstractmethod
    async def search_vectors(
        self,
        collection_name: str,
        query_vector: list[float],
        limit: int,
        filters: dict[str, object] | None = None,
    ) -> list[SearchHit]:
        ...


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or len(a) == 0:
        raise ValueError("vectors must be non-empty and equal length")

    dot = sum(x * y for x, y in zip(a, b, strict=True))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(y * y for y in b))
    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0
    return dot / (mag_a * mag_b)


def mock_embedding(text: str, dimension: int | None = None) -> list[float]:
    dim = dimension if dimension is not None else settings.VECTOR_DIMENSION
    digest = sha256(text.encode("utf-8")).digest()
    vec: list[float] = []
    for i in range(dim):
        byte = digest[i % len(digest)]
        vec.append(float(byte) / 255.0)
    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0.0:
        return [0.0] * dim
    return [v / norm for v in vec]


class InMemoryVectorStore(VectorStorageClient):
    def __init__(self) -> None:
        self._collections: dict[str, dict[str, VectorRecord]] = {}

    async def upsert_vectors(self, collection_name: str, records: list[VectorRecord]) -> int:
        store = self._collections.setdefault(collection_name, {})
        for record in records:
            store[record.id] = record
        logger.info("upserted %d vectors into %s", len(records), collection_name)
        return len(records)

    async def search_vectors(
        self,
        collection_name: str,
        query_vector: list[float],
        limit: int,
        filters: dict[str, object] | None = None,
    ) -> list[SearchHit]:
        store = self._collections.get(collection_name, {})
        hits: list[SearchHit] = []
        for record in store.values():
            if filters and not _matches_filters(record.payload, filters):
                continue
            hits.append(
                SearchHit(
                    id=record.id,
                    score=cosine_similarity(query_vector, record.vector),
                    payload=record.payload,
                )
            )
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:limit]


def _matches_filters(payload: dict[str, object], filters: dict[str, object]) -> bool:
    for key, value in filters.items():
        if payload.get(key) != value:
            return False
    return True


def get_vector_store() -> VectorStorageClient:
    provider = settings.VECTOR_STORE_PROVIDER
    if provider == "memory":
        return InMemoryVectorStore()
    raise ValueError(f"Unsupported VECTOR_STORE_PROVIDER: {provider!r} (supported: 'memory')")
