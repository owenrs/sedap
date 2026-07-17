import os

os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from app.api.v1.chat import router as chat_router
from app.api.v1.query import router as query_router
from app.api.v1.search import router as search_router
from app.core.config import get_settings
from app.main import app
from app.services.chunker import chunk_text


def test_settings_loads():
    settings = get_settings()
    assert settings.APP_ENV.value == "development"


def test_chunker_returns_records():
    records = chunk_text("hello world foo bar", source_name="test", chunk_size=5, chunk_overlap=2)
    assert len(records) > 0
    assert hasattr(records[0], "text_content")


def test_imports_resolve():
    assert app is not None
    assert search_router is not None
    assert query_router is not None
    assert chat_router is not None
