"""
Vehicle Memory
==============
Manages vehicle knowledge across sessions.

Responsibilities:
- Cache identified vehicles and their structured data.
- Persist vehicle knowledge to MongoDB.
- Support search by vehicle name, session, and query.
- Upsert (update-or-insert) vehicle entries.
- Provide vehicle context to the RAG pipeline.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class VehicleMemory:
    """
    In-process + MongoDB-backed vehicle knowledge store.
    """

    _cache: Dict[str, Dict[str, Any]] = {}   # vehicle_name (lower) → document
    _session_index: Dict[str, List[str]] = {}  # session_id → [vehicle_name]

    def __init__(self) -> None:
        self._mongo_enabled = self._check_mongo()

    # ------------------------------------------------------------------
    # Public Write
    # ------------------------------------------------------------------

    async def upsert(
        self,
        vehicle_name: str,
        session_id: Optional[str],
        confidence: float,
        source: str,
        attributes: Optional[Dict[str, Any]] = None,
        raw_context: Optional[str] = None,
    ) -> None:
        key = vehicle_name.strip().lower()
        existing = self._cache.get(key, {})

        now_iso = datetime.now(timezone.utc).isoformat()
        merged_attributes = {**existing.get("attributes", {}), **(attributes or {})}

        entry: Dict[str, Any] = {
            **existing,
            "vehicle_name": vehicle_name,
            "confidence": max(confidence, existing.get("confidence", 0.0)),
            "source": source,
            "last_seen": now_iso,
            # Task 6: timestamps — only set specs_updated_at on first write
            "specs_updated_at": existing.get("specs_updated_at") or now_iso,
            "last_scraped_at": now_iso if source not in ("mongodb", "cache") else existing.get("last_scraped_at"),
            "price_updated_at": existing.get("price_updated_at"),   # preserved; updated via update_price()
            "attributes": merged_attributes,
            # Flatten attributes as top-level fields too, so consumers that
            # read mongo_doc.get("engine") / mongo_doc.get("horsepower") etc.
            # directly (without digging into "attributes") still find them.
            **merged_attributes,
            "raw_context": raw_context or existing.get("raw_context", ""),
            "sessions": list(
                set(existing.get("sessions", []) + ([session_id] if session_id else []))
            ),
        }

        self._cache[key] = entry

        if session_id:
            if session_id not in self._session_index:
                self._session_index[session_id] = []
            if vehicle_name not in self._session_index[session_id]:
                self._session_index[session_id].append(vehicle_name)

        await self._persist_vehicle(entry)

    async def update_price(self, vehicle_name: str, price_data: Dict[str, Any]) -> None:
        """Task 6/7: Update price fields and price_updated_at timestamp.

        price_data can contain: price, msrp, dealer_price, average_market_price,
        currency, sources (list of {url, title, domain}).
        """
        key = vehicle_name.strip().lower()
        now_iso = datetime.now(timezone.utc).isoformat()

        update_fields = {
            k: v for k, v in price_data.items()
            if k in ("price", "msrp", "dealer_price", "average_market_price", "currency", "sources")
            and v
        }
        update_fields["price_updated_at"] = now_iso

        if key in self._cache:
            self._cache[key].update(update_fields)

        # Also persist to MongoDB
        try:
            from data.database.mongodb.vehicle import VehicleCollection  # type: ignore
            vc = VehicleCollection()
            await asyncio.get_event_loop().run_in_executor(
                None,
                vc.update_price_field,
                vehicle_name,
                price_data.get("price", ""),
                now_iso,
                update_fields,
            )
        except Exception as exc:
            logger.warning("Failed to update price in MongoDB for '%s': %s", vehicle_name, exc)

    # ------------------------------------------------------------------
    # Public Read
    # ------------------------------------------------------------------

    async def get_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        names = self._session_index.get(session_id, [])
        results = []
        for name in names:
            entry = self._cache.get(name.lower())
            if entry:
                results.append(entry)
        return results

    async def get_by_name(
        self, vehicle_name: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        key = vehicle_name.strip().lower()
        entry = self._cache.get(key)
        if entry:
            return [entry]

        # Try MongoDB
        return await self._search_mongo_by_name(vehicle_name, limit)

    async def search_knowledge(
        self,
        vehicle_name: Optional[str],
        query: str,
    ) -> List[Dict[str, Any]]:
        """
        Search cached vehicle knowledge for content matching the query.
        """
        query_lower = query.lower()
        results: List[Dict[str, Any]] = []

        candidates = (
            [self._cache.get(vehicle_name.strip().lower())]
            if vehicle_name and vehicle_name.strip().lower() in self._cache
            else list(self._cache.values())
        )

        for entry in candidates:
            if entry is None:
                continue
            raw = entry.get("raw_context", "").lower()
            attrs_str = str(entry.get("attributes", {})).lower()
            if query_lower in raw or query_lower in attrs_str:
                results.append({
                    **entry,
                    "score": 0.7,
                    "confidence": entry.get("confidence", 0.5),
                })

        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results[:20]

    # ------------------------------------------------------------------
    # Private: MongoDB Integration
    # ------------------------------------------------------------------

    def _check_mongo(self) -> bool:
        try:
            from data.database.mongodb.mongodb import MongoDBManager  # type: ignore
            return True
        except ImportError:
            logger.warning("MongoDB module not importable — VehicleMemory running in-memory only.")
            return False

    async def _persist_vehicle(self, entry: Dict[str, Any]) -> None:
        if not self._mongo_enabled:
            return
        try:
            from data.database.mongodb.vehicle import VehicleCollection  # type: ignore
            vc = VehicleCollection()
            await asyncio.get_event_loop().run_in_executor(
                None, vc.upsert, entry
            )
        except Exception as exc:
            logger.warning("Failed to persist vehicle to MongoDB: %s", exc)

    async def _search_mongo_by_name(
        self, vehicle_name: str, limit: int
    ) -> List[Dict[str, Any]]:
        if not self._mongo_enabled:
            return []
        try:
            from data.database.mongodb.vehicle import VehicleCollection  # type: ignore
            vc = VehicleCollection()
            results = await asyncio.get_event_loop().run_in_executor(
                None, vc.find_by_name, vehicle_name, limit
            )
            for r in results or []:
                key = r.get("vehicle_name", "").lower()
                self._cache[key] = r
            return results or []
        except Exception as exc:
            logger.warning("MongoDB vehicle search failed: %s", exc)
            return []