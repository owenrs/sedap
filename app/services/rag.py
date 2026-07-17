import logging

from pydantic import BaseModel, Field

from app.core.memory import BaseMemoryStore, ChatMessage
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

CONDENSE_SYSTEM = (
    "You are a query condensation engine. Given the conversation history and the "
    "latest user message, rewrite it as a single, self-contained search query that "
    "captures the user's intent and any context from prior turns. Output ONLY the "
    "condensed query text, with no commentary."
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
        memory_store: BaseMemoryStore | None = None,
        collection: str = COLLECTION_NAME,
        top_k: int = DEFAULT_TOP_K,
    ) -> None:
        self._vector_store = vector_store
        self._embedding_service = embedding_service
        self._llm_service = llm_service
        self._memory_store = memory_store
        self._collection = collection
        self._top_k = top_k

    async def answer(
        self,
        user_query: str,
        session_id: str | None = None,
    ) -> RAGResponsePayload:
        condensed_query = await self._condense(user_query, session_id)

        vectors = await self._embedding_service.generate_embeddings([condensed_query])
        query_vector = vectors[0]

        hits: list[SearchHit] = await self._vector_store.search_hybrid(
            self._collection, condensed_query, query_vector, limit=self._top_k
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

        if session_id and self._memory_store is not None:
            await self._memory_store.add_message(
                session_id, ChatMessage(role="user", content=user_query)
            )
            await self._memory_store.add_message(
                session_id, ChatMessage(role="assistant", content=answer)
            )

        return RAGResponsePayload(
            answer=answer,
            references=references,
            context_used=bool(context),
        )

    async def _condense(self, user_query: str, session_id: str | None) -> str:
        if not session_id or self._memory_store is None:
            return user_query
        history = await self._memory_store.get_history(session_id)
        if not history:
            return user_query

        transcript = "\n".join(f"{m.role}: {m.content}" for m in history)
        condense_prompt = f"History:\n{transcript}\n\nLatest message:\n{user_query}"
        condensed = await self._llm_service.generate_response(
            condense_prompt, system_message=CONDENSE_SYSTEM
        )
        logger.info("condensed session %s query: %r", session_id, condensed[:80])
        return condensed.strip() or user_query
