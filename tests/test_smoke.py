import os

os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from app.core.config import get_settings
from app.core.entities import ExtractedEntities
from app.core.memory import ChatMessage, BaseMemoryStore, InMemoryMemoryStore
from app.core.queue import JobQueue, InMemoryQueue
from app.core.vector_store import VectorStorageClient, VectorRecord, InMemoryVectorStore
from app.services.embeddings import EmbeddingService, LocalEmbeddingProvider, OpenAIEmbeddingProvider
from app.services.llm import LLMService, MockLLMProvider, OpenAILLMProvider
from app.services.rag import RAGOrchestrator, RAGResponsePayload
from app.services.chunker import ChunkRecord, chunk_text
from app.services.extractor import ExtractedEntities as ExtractorEntities
from app.services.ingestion import extract_document
from app.api.v1.search import router as search_router
from app.api.v1.query import router as query_router
from app.api.v1.chat import router as chat_router
from app.main import app


def test_settings_loads():
    settings = get_settings()
    assert settings.APP_ENV.value == "development"


def test_chunker_returns_records():
    records = chunk_text("hello world foo bar", chunk_size=5, chunk_overlap=2)
    assert len(records) > 0
    assert hasattr(records[0], "text_content")


def test_imports_resolve():
    assert app is not None
    assert search_router is not None
    assert query_router is not None
    assert chat_router is not None
