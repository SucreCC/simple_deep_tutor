from .base_session_manager import BaseSessionManager
from .protocol import SessionStoreProtocol
from .sqlite_store import (
    SQLiteSessionStore,
    get_sqlite_session_store,
    make_imported_session_id,
)
from .turn_runtime import TurnRuntimeManager, get_turn_runtime_manager


def get_session_store() -> SessionStoreProtocol:
    """
    Return the active session store backend.

    When integrations.pocketbase_url is configured, returns a
    PocketBaseSessionStore. Otherwise falls back to the local
    SQLiteSessionStore (default, zero-config behaviour).
    """
    from deeptutor.services.pocketbase_client import is_pocketbase_enabled

    if is_pocketbase_enabled():
        from .pocketbase_store import PocketBaseSessionStore

        return PocketBaseSessionStore()
    return get_sqlite_session_store()


__all__ = [
    # "BaseSessionManager",
    "SessionStoreProtocol",
    # "SQLiteSessionStore",
    "TurnRuntimeManager",
    "get_session_store",
    # "get_sqlite_session_store",
    # "get_turn_runtime_manager",
    # "make_imported_session_id",
]
