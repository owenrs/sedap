import asyncio
import logging

from app.core.config import settings
from app.core.jobs import JobResult
from app.core.vector_store import VectorRecord, VectorStorageClient
from app.services.chunker import chunk_text
from app.services.embeddings import EmbeddingService, get_embedding_service
from app.services.extractor import get_extractor

logger = logging.getLogger("sedap.ingestion")

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}
COLLECTION_NAME = "chunks"


async def extract_document(
    job_id: str,
    payload: dict[str, object],
    vector_store: VectorStorageClient | None = None,
    embedding_service: EmbeddingService | None = None,
) -> JobResult:
    filename = str(payload.get("filename", "unknown"))
    raw_size = payload.get("size", 0)
    size = int(raw_size) if isinstance(raw_size, (int, float, str)) else 0
    raw_text = str(payload.get("raw_text", ""))

    logger.info("job %s: extracting %s (%d bytes)", job_id, filename, size)
    await asyncio.sleep(settings.MOCK_EXTRACTION_DELAY_SECONDS)

    chunks = chunk_text(raw_text, source_name=filename)

    extractor = get_extractor()
    for chunk in chunks:
        entities = extractor.extract(chunk.text_content)
        chunk.metadata["entities"] = entities.model_dump()

    if vector_store is not None:
        embedder = embedding_service or get_embedding_service()
        texts = [chunk.text_content for chunk in chunks]
        vectors = await embedder.generate_embeddings(texts)
        records = [
            VectorRecord(
                id=chunk.chunk_id,
                vector=vectors[i],
                payload={
                    "chunk_id": chunk.chunk_id,
                    "index": chunk.index,
                    "text_content": chunk.text_content,
                    "source": filename,
                    "metadata": chunk.metadata,
                },
            )
            for i, chunk in enumerate(chunks)
        ]
        await vector_store.upsert_vectors(COLLECTION_NAME, records)
        logger.info("job %s: indexed %d vectors (provider=%s)", job_id, len(records), settings.EMBEDDING_PROVIDER)

    logger.info("job %s: produced %d chunks with entity enrichment", job_id, len(chunks))

    return JobResult(
        extracted_text=raw_text,
        chunks=chunks,
        metadata={
            "filename": filename,
            "size_bytes": size,
            "chunk_count": len(chunks),
            "chunk_size": settings.CHUNK_SIZE,
            "chunk_overlap": settings.CHUNK_OVERLAP,
            "embedding_provider": settings.EMBEDDING_PROVIDER,
            "indexed": vector_store is not None,
        },
    )
