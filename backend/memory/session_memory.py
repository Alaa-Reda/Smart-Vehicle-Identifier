"""
Session Memory
==============
Manages per-session conversation state.

Responsibilities:
- Store and retrieve conversation turns per session.
- Maintain context window for the RAG system.
- Cache session data in-process for low latency.
- Persist to MongoDB for durability.
- Support search across history.
- Support export and deletion.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Maximum turns kept in memory per session before summarization
MAX_IN_MEMORY_TURNS = 50


class SessionMemory:
    """
    Thread-safe session memory with in-process cache and MongoDB persistence.
    """

    # Shared in-process cache: session_id → list of turns
    _cache: Dict[str, List[Dict[str, Any]]] = {}
    _meta: Dict[str, Dict[str, Any]] = {}
    _lock: asyncio.Lock = asyncio.Lock()

    def __init__(self) -> None:
        self._mongo_enabled = self._check_mongo()

    # ------------------------------------------------------------------
    # Public Write
    # ------------------------------------------------------------------

    async def add_turn(
        self,
        session_id: Optional[str],
        user_message: str,
        assistant_message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        if not session_id:
            return ""

        turn = {
            "_id": str(uuid.uuid4()),
            "session_id": session_id,
            "role_user": user_message,
            "role_assistant": assistant_message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }

        async with self._lock:
            if session_id not in self._cache:
                self._cache[session_id] = []
            self._cache[session_id].append(turn)

            # Trim cache to MAX_IN_MEMORY_TURNS
            if len(self._cache[session_id]) > MAX_IN_MEMORY_TURNS:
                self._cache[session_id] = self._cache[session_id][-MAX_IN_MEMORY_TURNS:]

        await self._persist_turn(turn)
        return turn["_id"]

    async def set_last_vehicle(
        self, session_id: str, vehicle_name: Optional[str]
    ) -> None:
        async with self._lock:
            if session_id not in self._meta:
                self._meta[session_id] = {}
            self._meta[session_id]["last_vehicle"] = vehicle_name

    # ------------------------------------------------------------------
    # Public Read
    # ------------------------------------------------------------------

    async def get_context(self, session_id: Optional[str]) -> Dict[str, Any]:
        if not session_id:
            return {}

        meta = self._meta.get(session_id, {})
        turns = self._cache.get(session_id, [])
        recent_turns = turns[-10:] if turns else []

        return {
            "session_id": session_id,
            "last_vehicle": meta.get("last_vehicle"),
            "recent_turns": recent_turns,
            "turn_count": len(turns),
        }

    async def get_history(
        self,
        session_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> Optional[Dict[str, Any]]:
        turns = self._cache.get(session_id)

        if turns is None:
            # Attempt to load from MongoDB
            turns = await self._load_from_mongo(session_id)
            if turns is None:
                return None

        total = len(turns)
        start = (page - 1) * page_size
        end = start + page_size
        page_turns = turns[start:end]

        return {
            "session_id": session_id,
            "total": total,
            "page": page,
            "page_size": page_size,
            "turns": page_turns,
        }

    async def get_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        ctx = await self.get_context(session_id)
        if not ctx:
            return None

        turns = self._cache.get(session_id, [])
        if not turns:
            return None

        vehicles_mentioned: set[str] = set()
        for turn in turns:
            meta = turn.get("metadata", {})
            # Collect vehicle names from metadata
            if meta.get("vehicle_name"):
                vehicles_mentioned.add(meta["vehicle_name"])

        return {
            "session_id": session_id,
            "turn_count": len(turns),
            "last_vehicle": ctx.get("last_vehicle"),
            "vehicles_discussed": list(vehicles_mentioned),
            "started_at": turns[0]["timestamp"] if turns else None,
            "last_activity": turns[-1]["timestamp"] if turns else None,
        }

    async def search(
        self,
        keyword: str,
        session_id: Optional[str],
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        keyword_lower = keyword.lower()
        results: List[Dict[str, Any]] = []

        if session_id:
            sessions_to_search = {session_id: self._cache.get(session_id, [])}
        else:
            sessions_to_search = self._cache

        for sid, turns in sessions_to_search.items():
            for turn in turns:
                if (
                    keyword_lower in turn.get("role_user", "").lower()
                    or keyword_lower in turn.get("role_assistant", "").lower()
                ):
                    results.append({**turn, "session_id": sid})
                    if len(results) >= limit:
                        break
            if len(results) >= limit:
                break

        return results

    async def export_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        summary = await self.get_summary(session_id)
        if summary is None:
            return None

        turns = self._cache.get(session_id, [])
        return {
            "session_id": session_id,
            "summary": summary,
            "turns": turns,
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Public Delete
    # ------------------------------------------------------------------

    async def clear(self, session_id: str) -> None:
        async with self._lock:
            self._cache.pop(session_id, None)
            self._meta.pop(session_id, None)

    async def delete_session(self, session_id: str) -> int:
        async with self._lock:
            turns = self._cache.pop(session_id, [])
            self._meta.pop(session_id, None)
        deleted_count = len(turns)
        await self._delete_from_mongo_by_session(session_id)
        return deleted_count

    async def delete_message(self, message_id: str) -> bool:
        async with self._lock:
            for sid, turns in self._cache.items():
                for i, turn in enumerate(turns):
                    if turn.get("_id") == message_id:
                        del turns[i]
                        return True
        return False

    # ------------------------------------------------------------------
    # Private: MongoDB Integration
    # ------------------------------------------------------------------

    def _check_mongo(self) -> bool:
        try:
            from database.mongodb.mongodb import MongoDBManager  # type: ignore
            return True
        except ImportError:
            return False

    async def _persist_turn(self, turn: Dict[str, Any]) -> None:
        if not self._mongo_enabled:
            return
        try:
            from database.mongodb.history import HistoryCollection  # type: ignore
            history = HistoryCollection()
            await asyncio.get_event_loop().run_in_executor(
                None, history.insert, turn
            )
        except Exception as exc:
            logger.warning("Failed to persist turn to MongoDB: %s", exc)

    async def _load_from_mongo(
        self, session_id: str
    ) -> Optional[List[Dict[str, Any]]]:
        if not self._mongo_enabled:
            return None
        try:
            from database.mongodb.history import HistoryCollection  # type: ignore
            history = HistoryCollection()
            turns = await asyncio.get_event_loop().run_in_executor(
                None, history.get_by_session, session_id
            )
            if turns:
                async with self._lock:
                    self._cache[session_id] = turns
            return turns if turns else None
        except Exception as exc:
            logger.warning("Failed to load history from MongoDB: %s", exc)
            return None

    async def _delete_from_mongo_by_session(self, session_id: str) -> None:
        if not self._mongo_enabled:
            return
        try:
            from database.mongodb.history import HistoryCollection  # type: ignore
            history = HistoryCollection()
            await asyncio.get_event_loop().run_in_executor(
                None, history.delete_by_session, session_id
            )
        except Exception as exc:
            logger.warning("Failed to delete session from MongoDB: %s", exc)
