"""
Vehicle Collection

Handles all database operations related to vehicles.
"""

from __future__ import annotations

from typing import Any, Optional

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

    def find_by_name(self, vehicle_name: str, limit: int = 10) -> list[dict]:
        """
        Find vehicles by name (case-insensitive partial match).
        Used by VehicleMemory.get_by_name().
        """
        import re
        pattern = re.compile(re.escape(vehicle_name.strip()), re.IGNORECASE)
        cursor = self._collection.find({"vehicle_name": {"$regex": pattern}}).limit(limit)
        return list(cursor)

    def upsert(self, entry: dict) -> str:
        """
        Insert or update a vehicle document by vehicle_name.
        Used by VehicleMemory.upsert() for persistence.
        Returns the document _id as string.
        """
        vehicle_name = entry.get("vehicle_name", "")
        result = self._collection.update_one(
            {"vehicle_name": vehicle_name},
            {"$set": entry},
            upsert=True,
        )
        if result.upserted_id:
            return str(result.upserted_id)
        doc = self._collection.find_one({"vehicle_name": vehicle_name}, {"_id": 1})
        return str(doc["_id"]) if doc else ""

    def update_price_field(
        self,
        vehicle_name: str,
        price: str,
        price_updated_at: str,
        extra_fields: Optional[dict] = None,
    ) -> bool:
        """
        Task 6/7: Update price-related fields only.
        extra_fields can include: msrp, dealer_price, average_market_price, currency, sources
        """
        update_data: dict = {"price": price, "price_updated_at": price_updated_at}
        if extra_fields:
            for k in ("msrp", "dealer_price", "average_market_price", "currency", "sources"):
                if k in extra_fields and extra_fields[k]:
                    update_data[k] = extra_fields[k]

        result = self._collection.update_one(
            {"vehicle_name": vehicle_name},
            {"$set": update_data},
        )
        return result.modified_count > 0