from fastapi import APIRouter, Query, Request
from pydantic import BaseModel

from app.core.vector_store import SearchHit, VectorStorageClient
from app.services.embeddings import EmbeddingService

router = APIRouter(prefix="/api/v1", tags=["search"])


class SearchResultItem(BaseModel):
    id: str
    score: float
    text_content: str
    source: str | None = None
    metadata: dict[str, object] = {}


class SearchResultsPayload(BaseModel):
    query: str
    collection: str
    count: int
    results: list[SearchResultItem]


def _store(request: Request) -> VectorStorageClient:
    return request.app.state.vector_store  # type: ignore[no-any-return]


def _embedder(request: Request) -> EmbeddingService:
    return request.app.state.embedding_service  # type: ignore[no-any-return]


def _to_item(hit: SearchHit) -> SearchResultItem:
    payload = hit.payload
    source = payload.get("source")
    metadata = payload.get("metadata", {})
    return SearchResultItem(
        id=hit.id,
        score=round(hit.score, 6),
        text_content=str(payload.get("text_content", "")),
        source=source if isinstance(source, str) else None,
        metadata=metadata if isinstance(metadata, dict) else {},
    )


@router.get("/search", response_model=SearchResultsPayload)
async def search(
    request: Request,
    q: str = Query(..., min_length=1, description="Raw text query"),
    limit: int = Query(5, ge=1, le=100, description="Max number of matches"),
    collection: str = Query("chunks", description="Vector collection to search"),
) -> SearchResultsPayload:
    embedder = _embedder(request)
    vectors = await embedder.generate_embeddings([q])
    query_vector = vectors[0]

    store = _store(request)
    hits = await store.search_vectors(collection, query_vector, limit=limit)

    items = [_to_item(hit) for hit in hits]
    return SearchResultsPayload(
        query=q,
        collection=collection,
        count=len(items),
        results=items,
    )
