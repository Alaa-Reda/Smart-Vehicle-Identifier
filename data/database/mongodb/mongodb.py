"""
MongoDB Database Manager

Responsible for:
- Connecting to MongoDB
- Managing database lifecycle
- Providing collection instances

This module should be the only place where the MongoDB
connection is created.
"""

from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, PyMongoError


load_dotenv()


class MongoDBManager:
    """
    MongoDB connection manager.

    This class implements the Singleton Pattern to ensure that
    only one MongoDB connection exists during the application's
    lifetime.
    """

    _instance: Optional["MongoDBManager"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._client = None
            cls._instance._database = None

        return cls._instance

    def connect(self) -> None:
        """
        Establish a connection to MongoDB.
        """

        if self._client is not None:
            return

        mongo_uri = os.getenv("MONGODB_URI")
        database_name = os.getenv("MONGODB_DATABASE")

        if not mongo_uri:
            raise ValueError("Environment variable 'MONGODB_URI' not found.")

        if not database_name:
            raise ValueError("Environment variable 'MONGODB_DATABASE' not found.")

        try:
            self._client = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=5000
            )

            # Verify connection
            self._client.admin.command("ping")

            self._database = self._client[database_name]

            print("✅ Connected to MongoDB.")

        except ConnectionFailure as error:
            raise ConnectionError(
                f"Failed to connect to MongoDB: {error}"
            ) from error

    def disconnect(self) -> None:
        """
        Close the MongoDB connection.
        """

        if self._client is not None:
            self._client.close()

            self._client = None
            self._database = None

            print("MongoDB connection closed.")

    def get_database(self) -> Database:
        """
        Return the active database instance.
        """

        if self._database is None:
            self.connect()

        return self._database

    def get_collection(self, collection_name: str) -> Collection:
        """
        Return a MongoDB collection.

        Parameters
        ----------
        collection_name : str
            Name of the MongoDB collection.

        Returns
        -------
        Collection
        """

        return self.get_database()[collection_name]

    def collection_exists(self, collection_name: str) -> bool:
        """
        Check whether a collection exists.
        """

        return collection_name in self.get_database().list_collection_names()

    def health_check(self) -> bool:
        """
        Verify that MongoDB is reachable.
        """

        try:
            self._client.admin.command("ping")
            return True

        except PyMongoError:
            return False