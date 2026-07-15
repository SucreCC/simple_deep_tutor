import asyncio
import json
import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws")
async def unified_websocket(ws: WebSocket) -> None:
    await ws.accept()
    closed = False
    subscription_tasks: dict[str, asyncio.Task[None]] = {}

    async def safe_send(data: dict[str, Any]) -> None:
        nonlocal closed
        if closed:
            return
        try:
            await ws.send_text(json.dumps(data, ensure_ascii=False, default=str))
        except Exception:
            closed = True

    async def stop_subscription(key: str) -> None:
        task = subscription_tasks.pop(key, None)
        if task is None:
            return
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    async def subscribe_turn(turn_id: str, after_seq: int = 0) -> None:
        from deeptutor.services.session import get_turn_runtime_manager

        async def _forward() -> None:
            runtime = get_turn_runtime_manager()
            async for event in runtime.subscribe_turn(turn_id, after_seq=after_seq):
                await safe_send(event)

            await stop_subscription(turn_id)
            subscription_tasks[turn_id] = asyncio.create_task(_forward())