import logging

from pydantic import BaseModel, Field

from app.core.vector_store import SearchHit, VectorStorageClient
from app.services.embeddings import EmbeddingService
from app.services.llm import LLMService

logger = logging.getLogger("sedap.rag")

COLLECTION_NAME = "chunks"
DEFAULT_TOP_K = 5

SYSTEM_MESSAGE = (
    "You are SEDAP, a precise document analysis assistant. Answer the user's "
    "question using ONLY the provided context passages. Cite the source material "
    "where possible. If the context does not contain the answer, say so explicitly."
)


class RAGReference(BaseModel):
    chunk_id: str
    score: float


class RAGResponsePayload(BaseModel):
    answer: str
    references: list[RAGReference] = Field(default_factory=list)
    context_used: bool = False


class RAGOrchestrator:
    def __init__(
        self,
        vector_store: VectorStorageClient,
        embedding_service: EmbeddingService,
        llm_service: LLMService,
        collection: str = COLLECTION_NAME,
        top_k: int = DEFAULT_TOP_K,
    ) -> None:
        self._vector_store = vector_store
        self._embedding_service = embedding_service
        self._llm_service = llm_service
        self._collection = collection
        self._top_k = top_k

    async def answer(self, user_query: str) -> RAGResponsePayload:
        vectors = await self._embedding_service.generate_embeddings([user_query])
        query_vector = vectors[0]

        hits: list[SearchHit] = await self._vector_store.search_hybrid(
            self._collection, user_query, query_vector, limit=self._top_k
        )

        context_blocks = [
            f"[{hit.id}]\n{str(hit.payload.get('text_content', ''))}" for hit in hits
        ]
        context = "\n\n".join(context_blocks)

        if context:
            prompt = f"Context:\n{context}\n\nQuestion:\n{user_query}"
            references = [
                RAGReference(chunk_id=hit.id, score=round(hit.score, 6)) for hit in hits
            ]
        else:
            prompt = f"Question:\n{user_query}"
            references = []

        answer = await self._llm_service.generate_response(
            prompt, system_message=SYSTEM_MESSAGE
        )

        return RAGResponsePayload(
            answer=answer,
            references=references,
            context_used=bool(context),
        )
