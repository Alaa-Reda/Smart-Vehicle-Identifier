"""
Comparison Collection

Handles all database operations related to vehicle comparisons.
"""

from __future__ import annotations

from typing import Any

from bson import ObjectId
from pymongo.collection import Collection

from .mongodb import MongoDBManager


class ComparisonCollection:
    """
    Vehicle comparison MongoDB collection handler.
    """

    COLLECTION_NAME = "comparisons"

    def __init__(self) -> None:
        self._collection: Collection = (
            MongoDBManager().get_collection(self.COLLECTION_NAME)
        )

    def insert(self, comparison_data: dict[str, Any]) -> str:
        """
        Insert a new comparison document.
        """
        result = self._collection.insert_one(comparison_data)
        return str(result.inserted_id)

    def find_by_id(self, comparison_id: str) -> dict[str, Any] | None:
        """
        Find a comparison document by ObjectId.
        """
        return self._collection.find_one(
            {"_id": ObjectId(comparison_id)}
        )

    def find_by_session(
        self,
        session_id: str
    ) -> list[dict[str, Any]]:
        """
        Return all comparisons for a session.
        """
        return list(
            self._collection.find(
                {"session_id": session_id}
            )
        )

    def find_all(self) -> list[dict[str, Any]]:
        """
        Return all comparison documents.
        """
        return list(self._collection.find())

    def update(
        self,
        comparison_id: str,
        updated_data: dict[str, Any]
    ) -> bool:
        """
        Update a comparison document.
        """
        result = self._collection.update_one(
            {"_id": ObjectId(comparison_id)},
            {"$set": updated_data},
        )

        return result.modified_count > 0

    def delete(self, comparison_id: str) -> bool:
        """
        Delete a comparison document.
        """
        result = self._collection.delete_one(
            {"_id": ObjectId(comparison_id)}
        )

        return result.deleted_count > 0

    def count(self) -> int:
        """
        Return total number of comparison documents.
        """
        return self._collection.count_documents({})