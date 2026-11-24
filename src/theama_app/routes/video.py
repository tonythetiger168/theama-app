# SPDX-License-Identifier: Apache-2.0
"""Film line API: POST /api/video -> job (4K 30s MP4 target)."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from theama_app.jobs import queue

router = APIRouter(prefix="/api", tags=["video"])


class VideoRequest(BaseModel):
    prompt: str = Field(min_length=1)
    seconds: int = Field(default=5, ge=1, le=30)
    resolution: str = Field(default="720p", pattern="^(720p|2K|4K)$")
    audio: bool = True
    seed: int | None = None


@router.post("/video")
async def create_video_job(req: VideoRequest):
    job = queue.submit("video", req.model_dump())
    return {"job_id": job.id, "status": job.status.value}
