from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.core.memory import BaseMemoryStore
from app.core.vector_store import VectorStorageClient
from app.services.embeddings import EmbeddingService
from app.services.llm import LLMService
from app.services.rag import RAGOrchestrator, RAGResponsePayload

router = APIRouter(prefix="/api/v1", tags=["chat"])


class ChatRequest(BaseModel):
    session_id: str
    message: str


def _orchestrator(request: Request, top_k: int) -> RAGOrchestrator:
    store: VectorStorageClient = request.app.state.vector_store
    embedder: EmbeddingService = request.app.state.embedding_service
    llm: LLMService = request.app.state.llm_service
    memory: BaseMemoryStore = request.app.state.memory_store
    return RAGOrchestrator(
        vector_store=store,
        embedding_service=embedder,
        llm_service=llm,
        memory_store=memory,
        top_k=top_k,
    )


@router.post("/chat", response_model=RAGResponsePayload)
async def chat(request: Request, body: ChatRequest) -> RAGResponsePayload:
    orchestrator = _orchestrator(request, 5)
    return await orchestrator.answer(body.message, session_id=body.session_id)
