import logging
import math
import re
from abc import ABC, abstractmethod
from hashlib import sha256

from pydantic import BaseModel, Field

from app.core.config import settings

logger = logging.getLogger("sedap.vector_store")

RRF_K = 60
_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


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

    @abstractmethod
    async def search_hybrid(
        self,
        collection_name: str,
        query_text: str,
        query_vector: list[float],
        limit: int,
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


def reciprocal_rank_fusion(
    rank_lists: list[list[str]], k: int = RRF_K
) -> dict[str, float]:
    fused: dict[str, float] = {}
    for rank_list in rank_lists:
        for rank, doc_id in enumerate(rank_list):
            fused[doc_id] = fused.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
    return fused


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
        self._bm25_corpus: dict[str, list[list[str]]] = {}
        self._bm25_ids: dict[str, list[str]] = {}

    async def upsert_vectors(self, collection_name: str, records: list[VectorRecord]) -> int:
        store = self._collections.setdefault(collection_name, {})
        corpus = self._bm25_corpus.setdefault(collection_name, [])
        ids = self._bm25_ids.setdefault(collection_name, [])

        existing_ids = set(ids)
        for record in records:
            is_new = record.id not in existing_ids
            store[record.id] = record
            tokens = _tokenize(str(record.payload.get("text_content", "")))
            if is_new:
                ids.append(record.id)
                corpus.append(tokens)
            else:
                idx = ids.index(record.id)
                corpus[idx] = tokens

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

    async def search_hybrid(
        self,
        collection_name: str,
        query_text: str,
        query_vector: list[float],
        limit: int,
    ) -> list[SearchHit]:
        store = self._collections.get(collection_name, {})
        if not store:
            return []

        dense_hits = await self.search_vectors(collection_name, query_vector, limit=len(store))
        dense_ranks = [hit.id for hit in dense_hits]

        ids = self._bm25_ids.get(collection_name, [])
        corpus = self._bm25_corpus.get(collection_name, [])
        sparse_ranks: list[str] = []
        if corpus:
            from rank_bm25 import BM25Okapi  # type: ignore[import-untyped]

            bm25 = BM25Okapi(corpus)
            tokens = _tokenize(query_text)
            if tokens:
                scores = bm25.get_scores(tokens)
                ordered = sorted(range(len(ids)), key=lambda i: scores[i], reverse=True)
                sparse_ranks = [ids[i] for i in ordered if scores[i] > 0.0]

        fused = reciprocal_rank_fusion([dense_ranks, sparse_ranks])
        ranked = sorted(fused.items(), key=lambda kv: kv[1], reverse=True)[:limit]

        return [
            SearchHit(id=doc_id, score=score, payload=store[doc_id].payload)
            for doc_id, score in ranked
        ]


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
