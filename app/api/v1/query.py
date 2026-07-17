from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.core.vector_store import VectorStorageClient
from app.services.embeddings import EmbeddingService
from app.services.llm import LLMService
from app.services.rag import RAGOrchestrator, RAGResponsePayload

router = APIRouter(prefix="/api/v1", tags=["rag"])


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


def _orchestrator(request: Request, top_k: int) -> RAGOrchestrator:
    store: VectorStorageClient = request.app.state.vector_store
    embedder: EmbeddingService = request.app.state.embedding_service
    llm: LLMService = request.app.state.llm_service
    return RAGOrchestrator(
        vector_store=store,
        embedding_service=embedder,
        llm_service=llm,
        top_k=top_k,
    )


@router.post("/query", response_model=RAGResponsePayload)
async def query(request: Request, body: QueryRequest) -> RAGResponsePayload:
    orchestrator = _orchestrator(request, body.top_k)
    return await orchestrator.answer(body.query)
