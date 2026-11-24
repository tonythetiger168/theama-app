# SPDX-License-Identifier: Apache-2.0
"""FastAPI application: routes + job-queue lifecycle + static demo UI."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from theama_app import __version__
from theama_app.jobs import queue
from theama_app.routes import avatar, image, video

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    queue.start()
    yield
    await queue.stop()


app = FastAPI(title="Theama App", version=__version__, lifespan=lifespan)
app.include_router(image.router)
app.include_router(video.router)
app.include_router(avatar.router)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/healthz")
def healthz():
    return {"status": "ok", "version": __version__}


@app.get("/api/jobs/{job_id}")
def job_status(job_id: str):
    job = queue.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="unknown job id")
    return {
        "job_id": job.id,
        "kind": job.kind,
        "status": job.status.value,
        "result": job.result,
    }


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")
