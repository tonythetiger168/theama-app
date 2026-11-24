# SPDX-License-Identifier: Apache-2.0
"""Avatar line API: WS /ws/avatar — real-time interactive session channel.

Scaffold behavior: accepts the socket, echoes a `session_open` frame with the
negotiated config, then replies `pending_engine` to every push until the
StreamingAvatarSession engine is wired (M6b).
"""

from __future__ import annotations

import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["avatar"])


@router.websocket("/ws/avatar")
async def avatar_session(ws: WebSocket):
    await ws.accept()
    await ws.send_text(json.dumps({
        "event": "session_open",
        "config": {"width": 1280, "height": 720, "fps": 25},
        "engine": "pending",  # StreamingAvatarSession lands in M6b
    }))
    try:
        while True:
            msg = await ws.receive_text()
            # TODO(M6b/M6c): route audio chunks -> push_audio, text -> push_instruction
            await ws.send_text(json.dumps({"event": "pending_engine", "echo_len": len(msg)}))
    except WebSocketDisconnect:
        pass
