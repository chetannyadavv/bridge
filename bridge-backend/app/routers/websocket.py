from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from fastapi.concurrency import run_in_threadpool

from app.database import SessionLocal
from app.services import dispute_service
from app.websocket.manager import manager
from app.websocket.snapshot import build_dispute_snapshot_messages

router = APIRouter()


@router.websocket("/ws/disputes/{dispute_id}")
async def dispute_socket(
    websocket: WebSocket,
    dispute_id: str,
    role: str = Query(default="analyst"),
) -> None:
    """
    One room per dispute (Requirement 1). No auth in this sprint, so the
    caller just declares its own role via ?role=cardholder|merchant|analyst
    — the same self-declared-role pattern the rest of the app already
    uses (see RoleContext on the frontend).

    There's no client -> server message protocol in this sprint (no chat,
    no typing indicators, no cursor sync) — this is a push-only channel.
    Anything a client sends is read and ignored, which is also how
    "invalid websocket messages" are handled gracefully: there's nothing
    to fail to parse, because nothing is parsed.
    """
    db = SessionLocal()
    try:
        dispute = await run_in_threadpool(dispute_service.get_dispute, db, dispute_id)
        if dispute is None:
            # Reject before accept() — the client sees a clean close
            # rather than a connection that silently never receives
            # anything. Handles "unknown dispute IDs" gracefully.
            await websocket.close(code=4404, reason="Dispute not found")
            return
        snapshot_messages = await run_in_threadpool(build_dispute_snapshot_messages, db, dispute_id)
    finally:
        db.close()

    connection_id = await manager.connect(dispute_id, websocket, role)

    # Send the newly (re)connected client a full snapshot immediately.
    # This is what makes reconnection "just work" (Requirement 6): the
    # client doesn't need a separate REST call to catch up after a drop
    # — the socket itself delivers current state as soon as it reopens.
    for message in snapshot_messages:
        await websocket.send_json(message)

    await manager.broadcast_presence(dispute_id)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    except Exception:
        # Any other transport-level error also just ends the connection
        # gracefully rather than crashing the server process.
        pass
    finally:
        manager.disconnect(dispute_id, connection_id)
        await manager.broadcast_presence(dispute_id)
