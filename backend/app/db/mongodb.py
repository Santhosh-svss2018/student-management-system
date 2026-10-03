"""
MongoDB Database Connection Module
Provides client initialization, lifecycle management, and connection testing.
"""

import logging
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from app.core.config import settings

import certifi
from app.db.init_db import init_db

logger = logging.getLogger("edumanage.db")


class MongoDBManager:
    """Manages the MongoDB client connection and database handle."""

    client: Optional[MongoClient] = None
    db: Optional[Database] = None

    def connect(self) -> bool:
        """
        Initializes the MongoDB client and tests connectivity.
        Returns True if connected, False if database is unavailable.
        """
        try:
            logger.info("Connecting to MongoDB at %s ...", settings.MONGODB_URL)
            mongo_kwargs = {
                "serverSelectionTimeoutMS": settings.MONGODB_SERVER_TIMEOUT_MS,
                "connectTimeoutMS": settings.MONGODB_SERVER_TIMEOUT_MS,
            }
            try:
                mongo_kwargs["tlsCAFile"] = certifi.where()
            except Exception:
                pass

            self.client = MongoClient(settings.MONGODB_URL, **mongo_kwargs)
            # Verify connectivity with a ping command
            self.client.admin.command("ping")
            self.db = self.client[settings.MONGODB_DATABASE]
            logger.info("Successfully connected to MongoDB database: '%s'", settings.MONGODB_DATABASE)
            
            # Initialize indexes on collections
            init_db(self.db)
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
            logger.warning("MongoDB is currently unavailable at %s: %s", settings.MONGODB_URL, exc)
            self.db = None
            return False
        except Exception as exc:
            logger.error("Unexpected error connecting to MongoDB: %s", exc)
            self.db = None
            return False

    def close(self) -> None:
        """Closes the MongoDB connection pool."""
        if self.client:
            logger.info("Closing MongoDB connection pool...")
            self.client.close()
            self.client = None
            self.db = None

    def ping(self) -> dict:
        """
        Executes a ping command to test the active database connection.
        Returns a dictionary with status and detail message.
        """
        if self.client is None:
            # Try to connect if client was not established
            connected = self.connect()
            if not connected:
                return {
                    "connected": False,
                    "error": f"Unable to reach MongoDB at {settings.MONGODB_URL}. Please ensure MongoDB service is running."
                }

        try:
            self.client.admin.command("ping")
            return {
                "connected": True,
                "database": settings.MONGODB_DATABASE
            }
        except Exception as exc:
            return {
                "connected": False,
                "error": str(exc)
            }


# Singleton manager instance
db_manager = MongoDBManager()


def get_database() -> Optional[Database]:
    """Returns the active MongoDB database instance."""
    if db_manager.db is None:
        db_manager.connect()
    return db_manager.db


def get_client() -> Optional[MongoClient]:
    """Returns the active MongoDB client instance."""
    if db_manager.client is None:
        db_manager.connect()
    return db_manager.client
