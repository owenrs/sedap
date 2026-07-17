import asyncio
import logging

from app.core.config import settings
from app.core.jobs import JobResult

logger = logging.getLogger("sedap.ingestion")

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


async def extract_document(job_id: str, payload: dict[str, object]) -> JobResult:
    filename = str(payload.get("filename", "unknown"))
    raw_size = payload.get("size", 0)
    size = int(raw_size) if isinstance(raw_size, (int, float, str)) else 0

    logger.info("job %s: mocking extraction for %s (%d bytes)", job_id, filename, size)
    await asyncio.sleep(settings.MOCK_EXTRACTION_DELAY_SECONDS)

    return JobResult(
        extracted_text="Extracted text content",
        metadata={
            "filename": filename,
            "size_bytes": size,
            "mock": True,
        },
    )
