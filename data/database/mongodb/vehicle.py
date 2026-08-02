"""
Vehicle Collection

Handles all database operations related to vehicles.
"""

from __future__ import annotations

from typing import Any

from bson import ObjectId
from pymongo.collection import Collection

from .mongodb import MongoDBManager


class VehicleCollection:
    """
    Vehicle MongoDB collection handler.
    """

    COLLECTION_NAME = "vehicles"

    def __init__(self) -> None:
        self._collection: Collection = (
            MongoDBManager().get_collection(self.COLLECTION_NAME)
        )

    def insert(self, vehicle_data: dict[str, Any]) -> str:
        """
        Insert a new vehicle document.

        Returns:
            str: Inserted document ID.
        """
        result = self._collection.insert_one(vehicle_data)
        return str(result.inserted_id)

    def find_by_id(self, vehicle_id: str) -> dict[str, Any] | None:
        """
        Find a vehicle by its ObjectId.
        """
        return self._collection.find_one(
            {"_id": ObjectId(vehicle_id)}
        )

    def find_all(self) -> list[dict[str, Any]]:
        """
        Return all vehicles.
        """
        return list(self._collection.find())

    def update(
        self,
        vehicle_id: str,
        updated_data: dict[str, Any]
    ) -> bool:
        """
        Update a vehicle document.
        """
        result = self._collection.update_one(
            {"_id": ObjectId(vehicle_id)},
            {"$set": updated_data},
        )

        return result.modified_count > 0

    def delete(self, vehicle_id: str) -> bool:
        """
        Delete a vehicle document.
        """
        result = self._collection.delete_one(
            {"_id": ObjectId(vehicle_id)}
        )

        return result.deleted_count > 0

    def count(self) -> int:
        """
        Return number of vehicles.
        """
        return self._collection.count_documents({})


