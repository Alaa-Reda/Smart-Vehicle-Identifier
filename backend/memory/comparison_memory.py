"""
Comparison Memory
=================
Stores and retrieves vehicle comparison results.

Responsibilities:
- Persist comparison results to MongoDB.
- Retrieve comparisons by session.
- Delete comparisons.
- Support future recommendation and analytics features.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ComparisonMemory:
    """
    Comparison result store with in-process cache + MongoDB persistence.
    """

    _cache: Dict[str, Dict[str, Any]] = {}           # comparison_id → document
    _session_index: Dict[str, List[str]] = {}         # session_id → [comparison_id]

    def __init__(self) -> None:
        self._mongo_enabled = self._check_mongo()

    # ------------------------------------------------------------------
    # Public Write
    # ------------------------------------------------------------------

    async def save(
        self,
        session_id: str,
        comparison: Dict[str, Any],
    ) -> str:
        comparison_id = str(uuid.uuid4())
        entry: Dict[str, Any] = {
            "_id": comparison_id,
            "session_id": session_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            **comparison,
        }

        self._cache[comparison_id] = entry

        if session_id not in self._session_index:
            self._session_index[session_id] = []
        self._session_index[session_id].append(comparison_id)

        await self._persist_comparison(entry)
        return comparison_id

    async def delete(self, comparison_id: str) -> bool:
        if comparison_id not in self._cache:
            return False

        entry = self._cache.pop(comparison_id)
        session_id = entry.get("session_id")

        if session_id and session_id in self._session_index:
            self._session_index[session_id] = [
                cid for cid in self._session_index[session_id]
                if cid != comparison_id
            ]

        await self._delete_from_mongo(comparison_id)
        return True

    # ------------------------------------------------------------------
    # Public Read
    # ------------------------------------------------------------------

    async def get_by_session(
        self, session_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        ids = self._session_index.get(session_id, [])
        results = [
            self._cache[cid] for cid in ids if cid in self._cache
        ]

        if not results:
            results = await self._load_from_mongo_by_session(session_id, limit)

        results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return results[:limit]

    async def get_by_id(self, comparison_id: str) -> Optional[Dict[str, Any]]:
        return self._cache.get(comparison_id)

    # ------------------------------------------------------------------
    # Private: MongoDB Integration
    # ------------------------------------------------------------------

    def _check_mongo(self) -> bool:
        try:
            from database.mongodb.mongodb import MongoDBManager  # type: ignore
            return True
        except ImportError:
            return False

    async def _persist_comparison(self, entry: Dict[str, Any]) -> None:
        if not self._mongo_enabled:
            return
        try:
            from database.mongodb.comparison import ComparisonCollection  # type: ignore
            cc = ComparisonCollection()
            await asyncio.get_event_loop().run_in_executor(None, cc.insert, entry)
        except Exception as exc:
            logger.warning("Failed to persist comparison to MongoDB: %s", exc)

    async def _delete_from_mongo(self, comparison_id: str) -> None:
        if not self._mongo_enabled:
            return
        try:
            from database.mongodb.comparison import ComparisonCollection  # type: ignore
            cc = ComparisonCollection()
            await asyncio.get_event_loop().run_in_executor(
                None, cc.delete_by_id, comparison_id
            )
        except Exception as exc:
            logger.warning("Failed to delete comparison from MongoDB: %s", exc)

    async def _load_from_mongo_by_session(
        self, session_id: str, limit: int
    ) -> List[Dict[str, Any]]:
        if not self._mongo_enabled:
            return []
        try:
            from database.mongodb.comparison import ComparisonCollection  # type: ignore
            cc = ComparisonCollection()
            results = await asyncio.get_event_loop().run_in_executor(
                None, cc.find_by_session, session_id, limit
            )
            for r in results or []:
                self._cache[r["_id"]] = r
            return results or []
        except Exception as exc:
            logger.warning("Failed to load comparisons from MongoDB: %s", exc)
            return []
