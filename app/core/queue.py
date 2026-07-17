import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Awaitable, Callable

from app.core.config import settings
from app.core.jobs import (
    JobResult,
    JobStatus,
    JobStatusPayload,
    new_job_id,
    utc_now,
)

logger = logging.getLogger("sedap.queue")

EnqueueResult = JobStatusPayload
WorkerFn = Callable[[str, dict[str, object]], Awaitable[JobResult]]


class JobQueue(ABC):
    @abstractmethod
    async def enqueue_job(self, task_name: str, payload: dict[str, object]) -> JobStatusPayload:
        ...

    @abstractmethod
    async def get_job_status(self, job_id: str) -> JobStatusPayload | None:
        ...

    @abstractmethod
    async def start(self, worker: WorkerFn) -> None:
        ...

    @abstractmethod
    async def stop(self) -> None:
        ...


class InMemoryQueue(JobQueue):
    def __init__(self) -> None:
        self._queue: asyncio.Queue[tuple[str, dict[str, object]]] = asyncio.Queue()
        self._jobs: dict[str, JobStatusPayload] = {}
        self._worker_task: asyncio.Task[None] | None = None
        self._worker_fn: WorkerFn | None = None

    async def enqueue_job(self, task_name: str, payload: dict[str, object]) -> JobStatusPayload:
        job_id = new_job_id()
        now = utc_now()
        record = JobStatusPayload(
            job_id=job_id,
            status=JobStatus.pending,
            created_at=now,
            updated_at=now,
        )
        self._jobs[job_id] = record
        await self._queue.put((job_id, {"task_name": task_name, **payload}))
        return record

    async def get_job_status(self, job_id: str) -> JobStatusPayload | None:
        return self._jobs.get(job_id)

    async def start(self, worker: WorkerFn) -> None:
        if self._worker_task is not None:
            return
        self._worker_fn = worker
        self._worker_task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        if self._worker_task is not None:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
            self._worker_task = None

    async def _run_loop(self) -> None:
        assert self._worker_fn is not None
        while True:
            job_id, payload = await self._queue.get()
            record = self._jobs[job_id]
            record.status = JobStatus.processing
            record.updated_at = utc_now()
            try:
                record.result = await self._worker_fn(job_id, payload)
                record.status = JobStatus.completed
            except Exception as exc:  # noqa: BLE001 - surface any worker failure as job failure
                record.status = JobStatus.failed
                record.error = str(exc)
                logger.exception("job %s failed", job_id)
            finally:
                record.updated_at = utc_now()
                self._queue.task_done()


def get_queue() -> JobQueue:
    provider = settings.QUEUE_PROVIDER
    if provider == "memory":
        return InMemoryQueue()
    raise ValueError(f"Unsupported QUEUE_PROVIDER: {provider!r} (supported: 'memory')")
