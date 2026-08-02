"""
Vector Index Collection

Handles all database operations related to FAISS vector mappings.
"""

from __future__ import annotations

from typing import Any

from bson import ObjectId
from pymongo.collection import Collection

from .mongodb import MongoDBManager


class VectorIndexCollection:
    """
    MongoDB collection for mapping FAISS vector IDs
    to vehicle documents.
    """

    COLLECTION_NAME = "vector_index"

    def __init__(self) -> None:
        self._collection: Collection = (
            MongoDBManager().get_collection(self.COLLECTION_NAME)
        )

    def insert(self, document: dict[str, Any]) -> str:
        """
        Insert a new vector mapping.

        Returns
        -------
        str
            Inserted document ID.
        """
        result = self._collection.insert_one(document)
        return str(result.inserted_id)

    def find_by_id(self, document_id: str) -> dict[str, Any] | None:
        """
        Find mapping by MongoDB document ID.
        """
        return self._collection.find_one(
            {"_id": ObjectId(document_id)}
        )

    def find_by_vector_id(self, vector_id: int) -> dict[str, Any] | None:
        """
        Find mapping by FAISS vector ID.
        """
        return self._collection.find_one(
            {"vector_id": vector_id}
        )

    def find_by_vehicle_id(self, vehicle_id: str) -> dict[str, Any] | None:
        """
        Find mapping by vehicle ID.
        """
        return self._collection.find_one(
            {"vehicle_id": vehicle_id}
        )

    def update(
        self,
        document_id: str,
        data: dict[str, Any],
    ) -> bool:
        """
        Update a mapping.
        """
        result = self._collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": data},
        )
        return result.modified_count > 0

    def delete(self, document_id: str) -> bool:
        """
        Delete a mapping.
        """
        result = self._collection.delete_one(
            {"_id": ObjectId(document_id)}
        )
        return result.deleted_count > 0

    def count(self) -> int:
        """
        Return total number of mappings.
        """
        return self._collection.count_documents({})