# SPDX-License-Identifier: Apache-2.0
"""Async job queue: generation requests are accepted immediately and processed
by a background worker once the Theama engines are wired in (M1/M6a/M7a).

Until then jobs transition to `pending_engine` — a deliberate, visible state,
not a failure.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    PENDING_ENGINE = "pending_engine"  # accepted, but model engine not wired yet
    DONE = "done"
    FAILED = "failed"


@dataclass
class Job:
    kind: str                     # "image" | "video" | "avatar"
    payload: dict
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    status: JobStatus = JobStatus.QUEUED
    created_at: float = field(default_factory=time.time)
    result: dict | None = None


class JobQueue:
    """In-memory queue (single-process dev). Swap for Redis in production."""

    def __init__(self):
        self._jobs: dict[str, Job] = {}
        # asyncio.Queue binds to the running loop — create it lazily in start()
        # (the app lifespan), never at import time, or a singleton reused across
        # TestClient sessions / loops dies with "bound to a different event loop".
        self._queue: asyncio.Queue[Job] | None = None
        self._worker: asyncio.Task | None = None

    def submit(self, kind: str, payload: dict) -> Job:
        job = Job(kind=kind, payload=payload)
        self._jobs[job.id] = job
        if self._queue is not None:
            self._queue.put_nowait(job)
        return job

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    async def _run(self) -> None:
        while True:
            job = await self._queue.get()
            try:
                job.status = JobStatus.RUNNING
                job.result = await self._execute(job)
                job.status = JobStatus.DONE
            except NotImplementedError:
                # Engine not wired yet — expected until M1/M6a/M7a land.
                job.status = JobStatus.PENDING_ENGINE
            except Exception as exc:  # noqa: BLE001
                job.status = JobStatus.FAILED
                job.result = {"error": str(exc)}

    async def _execute(self, job: Job) -> dict:
        # TODO(engine): dispatch to theama.image / theama.inference / theama.avatar
        raise NotImplementedError(f"engine for '{job.kind}' not wired")

    def start(self) -> None:
        if self._worker is None or self._worker.done():
            self._queue = asyncio.Queue()
            self._worker = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._worker:
            self._worker.cancel()
            self._worker = None


queue = JobQueue()
