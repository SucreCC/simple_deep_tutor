import asyncio
from dataclasses import dataclass, field
from typing import Any

from deeptutor.services.session.protocol import SessionStoreProtocol


@dataclass
class _LiveSubscriber:
    queue: asyncio.Queue[dict[str, Any]]

@dataclass
class _TurnExecution:
    turn_id: str
    session_id: str
    capability: str
    payload: dict[str, Any]
    task: asyncio.Task[None] | None = None
    subscribers: list[_LiveSubscriber] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)
    next_seq: int = 1
    events_flushed: bool = False

class TurnRuntimeManager:
    def __init__(self, store:SessionStoreProtocol|None =None) -> None:
        from deeptutor.services.session import get_session_store
        self.store = store or get_session_store()
        self._lock = asyncio.Lock()
        self._executions: dict[str, _TurnExecution] = {}
        # Per-turn reply queues used by tools that pause the agentic
        # loop (e.g. ``ask_user``). Queue is created in ``_run_turn``
        # before the orchestrator is invoked and cleaned up in the
        # ``finally`` block, so callers of ``submit_user_reply`` see
        # ``False`` for any turn that is no longer awaiting input.
        # Each entry is a dict of shape:
        #   {"text": str, "answers": list[{"questionId": str, "text": str}] | None}
        # ``text`` is always present (flat fallback for legacy callers);
        # ``answers`` carries the structured per-question replies when the
        # frontend sends the v2 ``ask_user`` shape.
        self._reply_queues: dict[str, asyncio.Queue[dict[str, Any] | None]] = {}