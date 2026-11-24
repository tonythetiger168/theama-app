# Theama App

Web app + API layer for [Theama](https://github.com/tonythetiger168/theama) —
the open, fully permissive (Apache-2.0/MIT) audio-video generation stack.

Exposes Theama's three product lines over HTTP/WebSocket:

| Line | Endpoint | Backing model |
| --- | --- | --- |
| Film | `POST /api/video` | Wan 2.2 A14B + Extend-30s + 4K regenerate |
| Avatar | `WS /ws/avatar` | Wan-Animate + streaming session |
| Image | `POST /api/image` | Qwen-Image-2512 (quality) / Z-Image Turbo (fast) |

## Status

Scaffold stage: API surface, job queue and demo UI are wired end-to-end;
generation backends land with Theama milestones M1 / M6a / M7a (jobs return
`pending_engine` until then).

## Quick start

```bash
pip install -e .[dev]
pytest tests/                  # CPU-only smoke tests
uvicorn theama_app.server:app --reload --app-dir src
# open http://127.0.0.1:8000/
```

## Layout

```
src/theama_app/     FastAPI server, job queue, route modules, static demo UI
configs/            app configuration
scripts/            dev helpers
tests/              CPU-only API smoke tests (no GPU, no weights)
```

## License

Apache-2.0 (see `LICENSE`). Model weights are pulled by the user and remain
under their own licenses — see the Theama repo's `docs/license-risks.md`.
