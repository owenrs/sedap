import asyncio
import logging

from app.core.config import settings
from app.core.jobs import JobResult
from app.services.chunker import chunk_text

logger = logging.getLogger("sedap.ingestion")

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


async def extract_document(job_id: str, payload: dict[str, object]) -> JobResult:
    filename = str(payload.get("filename", "unknown"))
    raw_size = payload.get("size", 0)
    size = int(raw_size) if isinstance(raw_size, (int, float, str)) else 0
    raw_text = str(payload.get("raw_text", ""))

    logger.info("job %s: extracting %s (%d bytes)", job_id, filename, size)
    await asyncio.sleep(settings.MOCK_EXTRACTION_DELAY_SECONDS)

    chunks = chunk_text(raw_text, source_name=filename)
    logger.info("job %s: produced %d chunks", job_id, len(chunks))

    return JobResult(
        extracted_text=raw_text,
        chunks=chunks,
        metadata={
            "filename": filename,
            "size_bytes": size,
            "chunk_count": len(chunks),
            "chunk_size": settings.CHUNK_SIZE,
            "chunk_overlap": settings.CHUNK_OVERLAP,
        },
    )
