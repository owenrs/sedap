from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class ChunkRecord(BaseModel):
    chunk_id: str
    index: int
    text_content: str
    page_number: int | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class JobResult(BaseModel):
    extracted_text: str = ""
    chunks: list[ChunkRecord] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)


class JobStatusPayload(BaseModel):
    job_id: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    result: JobResult | None = None
    error: str | None = None


def new_job_id() -> str:
    return uuid4().hex


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
