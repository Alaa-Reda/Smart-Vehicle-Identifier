"""
Session Collection

Handles all database operations related to user sessions.
"""

from __future__ import annotations

from typing import Any

from bson import ObjectId
from pymongo.collection import Collection

from .mongodb import MongoDBManager


class SessionCollection:
    """
    Session MongoDB collection handler.
    """

    COLLECTION_NAME = "sessions"

    def __init__(self) -> None:
        self._collection: Collection = (
            MongoDBManager().get_collection(self.COLLECTION_NAME)
        )

    def insert(self, session_data: dict[str, Any]) -> str:
        """
        Insert a new session document.
        """
        result = self._collection.insert_one(session_data)
        return str(result.inserted_id)

    def find_by_id(self, session_id: str) -> dict[str, Any] | None:
        """
        Find a session by its ObjectId.
        """
        return self._collection.find_one(
            {"_id": ObjectId(session_id)}
        )

    def find_all(self) -> list[dict[str, Any]]:
        """
        Return all sessions.
        """
        return list(self._collection.find())

    def update(
        self,
        session_id: str,
        updated_data: dict[str, Any]
    ) -> bool:
        """
        Update a session document.
        """
        result = self._collection.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": updated_data},
        )

        return result.modified_count > 0

    def delete(self, session_id: str) -> bool:
        """
        Delete a session document.
        """
        result = self._collection.delete_one(
            {"_id": ObjectId(session_id)}
        )

        return result.deleted_count > 0

    def count(self) -> int:
        """
        Return total number of sessions.
        """
        return self._collection.count_documents({})