from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.api.v1 import router as v1_router
from app.core.config import settings
from app.core.queue import JobQueue, get_queue
from app.core.vector_store import VectorStorageClient, get_vector_store
from app.services.ingestion import extract_document


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    queue: JobQueue = get_queue()
    await queue.start(extract_document)
    app.state.queue = queue

    vector_store: VectorStorageClient = get_vector_store()
    app.state.vector_store = vector_store
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
