# SPDX-License-Identifier: Apache-2.0
"""Image line API: POST /api/image -> job; GET result via /api/jobs/{id}."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from theama_app.jobs import queue

router = APIRouter(prefix="/api", tags=["image"])


class ImageRequest(BaseModel):
    prompt: str = Field(min_length=1)
    mode: str = Field(default="quality", pattern="^(quality|fast)$")
    width: int = Field(default=1664, ge=256, le=4096)
    height: int = Field(default=928, ge=256, le=4096)
    seed: int | None = None


@router.post("/image")
async def create_image_job(req: ImageRequest):
    job = queue.submit("image", req.model_dump())
    return {"job_id": job.id, "status": job.status.value}
