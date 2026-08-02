"""
History Collection

Handles all database operations related to chat history.
"""

from __future__ import annotations

from typing import Any

from bson import ObjectId
from pymongo.collection import Collection

from .mongodb import MongoDBManager


class HistoryCollection:
    """
    Chat history MongoDB collection handler.
    """

    COLLECTION_NAME = "history"

    def __init__(self) -> None:
        self._collection: Collection = (
            MongoDBManager().get_collection(self.COLLECTION_NAME)
        )

    def insert(self, history_data: dict[str, Any]) -> str:
        """
        Insert a new chat history document.
        """
        result = self._collection.insert_one(history_data)
        return str(result.inserted_id)

    def find_by_id(self, history_id: str) -> dict[str, Any] | None:
        """
        Find a history document by ID.
        """
        return self._collection.find_one(
            {"_id": ObjectId(history_id)}
        )

    def find_by_session(
        self,
        session_id: str
    ) -> list[dict[str, Any]]:
        """
        Return all chat messages for a session.
        """
        return list(
            self._collection.find(
                {"session_id": session_id}
            )
        )

    def find_all(self) -> list[dict[str, Any]]:
        """
        Return all history documents.
        """
        return list(self._collection.find())

    def update(
        self,
        history_id: str,
        updated_data: dict[str, Any]
    ) -> bool:
        """
        Update a history document.
        """
        result = self._collection.update_one(
            {"_id": ObjectId(history_id)},
            {"$set": updated_data},
        )

        return result.modified_count > 0

    def delete(self, history_id: str) -> bool:
        """
        Delete a history document.
        """
        result = self._collection.delete_one(
            {"_id": ObjectId(history_id)}
        )

        return result.deleted_count > 0

    def delete_session_history(self, session_id: str) -> int:
        """
        Delete all messages for a session.
        """
        result = self._collection.delete_many(
            {"session_id": session_id}
        )

        return result.deleted_count

    def count(self) -> int:
        """
        Return total number of history documents.
        """
        return self._collection.count_documents({})