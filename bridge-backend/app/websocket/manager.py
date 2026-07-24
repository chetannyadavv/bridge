import asyncio
import uuid
from typing import Dict

from fastapi import WebSocket


class ConnectionManager:
    """
    Owns all active dispute websocket connections, grouped into one
    "room" per dispute_id — Requirement 1 ("Each dispute should have its
    own connection group"). Business logic (evidence, timeline,
    recommendations) lives entirely in app/services/*; this class only
    knows about sockets, rooms, and presence.
    """

    def __init__(self) -> None:
        # dispute_id -> { connection_id -> {"socket": WebSocket, "role": str} }
        self._rooms: Dict[str, Dict[str, dict]] = {}
        # dispute_id -> lock, serializing the "read latest state, then
        # broadcast" critical section so concurrent writers (Requirement 7)
        # can't have their broadcasts interleave out of order.
        self._locks: Dict[str, asyncio.Lock] = {}

    def lock_for(self, dispute_id: str) -> asyncio.Lock:
        return self._locks.setdefault(dispute_id, asyncio.Lock())

    async def connect(self, dispute_id: str, websocket: WebSocket, role: str) -> str:
        await websocket.accept()
        connection_id = uuid.uuid4().hex
        room = self._rooms.setdefault(dispute_id, {})
        room[connection_id] = {"socket": websocket, "role": role}
        return connection_id

    def disconnect(self, dispute_id: str, connection_id: str) -> None:
        room = self._rooms.get(dispute_id)
        if not room:
            return
        room.pop(connection_id, None)
        if not room:
            self._rooms.pop(dispute_id, None)
            self._locks.pop(dispute_id, None)

    def presence(self, dispute_id: str) -> list[str]:
        room = self._rooms.get(dispute_id, {})
        return sorted({conn["role"] for conn in room.values()})

    async def broadcast(self, dispute_id: str, message: dict) -> None:
        room = self._rooms.get(dispute_id, {})
        stale: list[str] = []
        for connection_id, conn in list(room.items()):
            try:
                await conn["socket"].send_json(message)
            except Exception:
                # A dead/broken socket shouldn't take the whole broadcast
                # down — drop it and let its own disconnect handler
                # (already running, or about to run) clean it up.
                stale.append(connection_id)
        for connection_id in stale:
            self.disconnect(dispute_id, connection_id)

    async def broadcast_presence(self, dispute_id: str) -> None:
        await self.broadcast(
            dispute_id,
            {"type": "presence_updated", "payload": {"roles": self.presence(dispute_id)}},
        )


# Single process-wide instance. Sprint 4 runs a single backend instance
# (per Architecture v1.1's "single backend instance only"), so in-memory
# room state is safe here — a multi-instance deployment would need a
# shared broker (e.g. Redis pub/sub) instead, which is explicitly out of
# scope for this sprint.
manager = ConnectionManager()
