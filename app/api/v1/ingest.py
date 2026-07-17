import os

from fastapi import APIRouter, File, HTTPException, Request, UploadFile, status

from app.core.queue import JobQueue
from app.services.ingestion import SUPPORTED_EXTENSIONS

router = APIRouter(prefix="/api/v1", tags=["ingestion"])


def _queue(request: Request) -> JobQueue:
    return request.app.state.queue  # type: ignore[no-any-return]


@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest(request: Request, file: UploadFile = File(...)) -> dict[str, object]:  # noqa: B008
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type {ext!r}; expected one of {sorted(SUPPORTED_EXTENSIONS)}",
        )

    contents = await file.read()
    queue = _queue(request)
    record = await queue.enqueue_job(
        "extract_document",
        {
            "filename": file.filename or "upload",
            "size": len(contents),
            "content_type": file.content_type or "",
        },
    )
    return {
        "job_id": record.job_id,
        "status": record.status.value,
        "accepted": True,
    }


@router.get("/tasks/{job_id}")
async def task_status(request: Request, job_id: str) -> dict[str, object]:
    record = await _queue(request).get_job_status(job_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown job_id {job_id!r}",
        )
    return record.model_dump(mode="json")
