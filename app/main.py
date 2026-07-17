from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.api.v1 import router as v1_router
from app.core.config import settings
from app.core.queue import JobQueue, get_queue
from app.core.vector_store import VectorStorageClient, get_vector_store
from app.services.embeddings import EmbeddingService, get_embedding_service
from app.services.ingestion import extract_document
from app.services.llm import LLMService, get_llm_service


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    queue: JobQueue = get_queue()
    vector_store: VectorStorageClient = get_vector_store()
    embedding_service: EmbeddingService = get_embedding_service()
    llm_service: LLMService = get_llm_service()
    app.state.vector_store = vector_store
    app.state.embedding_service = embedding_service
    app.state.llm_service = llm_service

    worker = lambda job_id, payload: extract_document(  # noqa: E731 - bound closure
        job_id, payload, vector_store=vector_store, embedding_service=embedding_service
    )
    await queue.start(worker)
    app.state.queue = queue
    try:
        yield
    finally:
        await queue.stop()


app = FastAPI(title="SEDAP", version="0.1.0", lifespan=lifespan)
app.include_router(v1_router)


@app.get("/")
async def root() -> dict[str, object]:
    return {
        "status": "ok",
        "service": "sedap",
        "app_env": settings.APP_ENV.value,
        "message": "placeholder endpoint",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}
