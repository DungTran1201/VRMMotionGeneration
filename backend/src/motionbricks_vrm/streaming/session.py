"""WebSocket motion streaming session manager.

Handles frame serialization, pacing, client subscriptions, and clean lifecycle.
"""

from __future__ import annotations

import asyncio
import json
from typing import Dict, Optional, Set
from fastapi import WebSocket, WebSocketDisconnect

from motionbricks_vrm.schemas.canonical_motion import (
    AnimationFrame,
    CanonicalHumanoidMotion,
)


class StreamingSessionManager:
    """Manages active WebSocket client connections and frame streaming."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.discard(websocket)

    async def stream_motion(
        self,
        websocket: WebSocket,
        motion: CanonicalHumanoidMotion,
        loop: bool = False,
        speed: float = 1.0,
    ) -> None:
        """Stream frames to a client respecting motion FPS and playback speed."""
        fps = motion.metadata.fps
        dt = (1.0 / fps) / max(speed, 0.1)

        # Send initial metadata header packet
        header = {
            "type": "motion_header",
            "schema": motion.schema_,
            "metadata": motion.metadata.model_dump(by_alias=True),
        }
        await websocket.send_text(json.dumps(header))

        while True:
            for frame in motion.frames:
                packet = {
                    "type": "motion_frame",
                    "frame": frame.model_dump(by_alias=True),
                }
                await websocket.send_text(json.dumps(packet))
                await asyncio.sleep(dt)

            if not loop:
                end_packet = {"type": "motion_ended"}
                await websocket.send_text(json.dumps(end_packet))
                break
