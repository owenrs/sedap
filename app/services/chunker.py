import logging

from pydantic import ValidationError

from app.core.config import settings
from app.core.jobs import ChunkRecord

logger = logging.getLogger("sedap.chunker")


def _normalize(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def chunk_text(
    text: str,
    source_name: str,
    *,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[ChunkRecord]:
    size = chunk_size if chunk_size is not None else settings.CHUNK_SIZE
    overlap = chunk_overlap if chunk_overlap is not None else settings.CHUNK_OVERLAP

    if overlap >= size:
        raise ValueError(
            f"CHUNK_OVERLAP ({overlap}) must be strictly less than CHUNK_SIZE ({size})"
        )

    content = _normalize(text)
    chunks: list[ChunkRecord] = []

    if not content:
        return chunks

    step = size - overlap
    start = 0
    index = 0
    while start < len(content):
        end = min(start + size, len(content))
        segment = content[start:end]
        try:
            record = ChunkRecord(
                chunk_id=f"chunk-{index:04d}",
                index=index,
                text_content=segment,
                page_number=None,
                metadata={"source": source_name, "char_start": start, "char_end": end},
            )
        except ValidationError as exc:  # pragma: no cover - defensive
            raise ValueError(f"invalid chunk record: {exc}") from exc
        chunks.append(record)
        if end == len(content):
            break
        start += step

    return chunks
