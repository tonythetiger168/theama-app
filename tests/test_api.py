# SPDX-License-Identifier: Apache-2.0
"""CPU-only API smoke tests — no GPU, no model weights."""

from fastapi.testclient import TestClient

from theama_app.server import app


def test_healthz():
    with TestClient(app) as c:
        r = c.get("/healthz")
        assert r.status_code == 200
        assert r.json()["version"] == "0.1.0"


def test_image_job_lifecycle():
    with TestClient(app) as c:
        r = c.post("/api/image", json={"prompt": "夜市霓虹招牌", "mode": "fast"})
        assert r.status_code == 200
        job_id = r.json()["job_id"]

        import time
        for _ in range(50):
            j = c.get(f"/api/jobs/{job_id}").json()
            if j["status"] not in ("queued", "running"):
                break
            time.sleep(0.05)
        # Engine not wired yet: the job must surface as pending_engine, never fail silently.
        assert j["status"] == "pending_engine"
        assert j["kind"] == "image"


def test_video_job_validation():
    with TestClient(app) as c:
        bad = c.post("/api/video", json={"prompt": "x", "seconds": 99})
        assert bad.status_code == 422
        ok = c.post("/api/video", json={"prompt": "霓虹雨中的貓", "seconds": 30, "resolution": "4K"})
        assert ok.status_code == 200


def test_unknown_job_404():
    with TestClient(app) as c:
        assert c.get("/api/jobs/nope").status_code == 404


def test_index_page_served():
    with TestClient(app) as c:
        r = c.get("/")
        assert r.status_code == 200
        assert "Theama App" in r.text


def test_avatar_websocket_scaffold():
    with TestClient(app) as c:
        with c.websocket_connect("/ws/avatar") as ws:
            hello = ws.receive_json()
            assert hello["event"] == "session_open"
            assert hello["config"]["height"] == 720
            ws.send_text("你好")
            reply = ws.receive_json()
            assert reply["event"] == "pending_engine"
