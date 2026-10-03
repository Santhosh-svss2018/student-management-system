"""
User Service Module
Encapsulates business logic, hashing, and database operations for User management.
"""

import logging
from typing import List, Optional, Union
from bson import ObjectId
from fastapi import HTTPException, status
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from app.core.security import get_password_hash
from app.models.user import UserCreate, UserInDB

logger = logging.getLogger("edumanage.services.user")


def get_user_by_email(db: Database, email: str) -> Optional[UserInDB]:
    """
    Finds a user document in MongoDB by normalized email address.
    """
    normalized_email = email.strip().lower()
    user_doc = db.users.find_one({"email": normalized_email})
    if user_doc:
        return UserInDB.model_validate(user_doc)
    return None


def get_user_by_id(db: Database, user_id: Union[str, ObjectId]) -> Optional[UserInDB]:
    """
    Finds a user document in MongoDB by its BSON ObjectId.
    """
    if isinstance(user_id, str):
        if not ObjectId.is_valid(user_id):
            return None
        object_id = ObjectId(user_id)
    else:
        object_id = user_id

    user_doc = db.users.find_one({"_id": object_id})
    if user_doc:
        return UserInDB.model_validate(user_doc)
    return None


def get_users(db: Database, skip: int = 0, limit: int = 50) -> List[UserInDB]:
    """
    Fetches a paginated list of user documents from MongoDB.
    """
    cursor = db.users.find().skip(skip).limit(limit)
    users = [UserInDB.model_validate(doc) for doc in cursor]
    return users


def create_user(db: Database, user_in: UserCreate) -> UserInDB:
    """
    Registers a new user with secure Argon2 password hashing.
    Enforces unique email constraints and handles duplicates gracefully.
    """
    normalized_email = str(user_in.email).strip().lower()

    # Pre-check email existence for immediate feedback
    existing_user = get_user_by_email(db, normalized_email)
    if existing_user:
        logger.warning("Attempted registration with already existing email: %s", normalized_email)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists.",
        )

    # Securely hash plaintext password with Argon2
    hashed_password = get_password_hash(user_in.password)

    # Prepare User database model
    user_db = UserInDB(
        full_name=user_in.full_name,
        email=normalized_email,
        hashed_password=hashed_password,
        role=user_in.role,
        is_active=user_in.is_active,
    )

    user_dict = user_db.model_dump(by_alias=True)

    try:
        db.users.insert_one(user_dict)
        logger.info("Successfully created user: %s (Role: %s)", normalized_email, user_in.role)
        return user_db
    except DuplicateKeyError as exc:
        logger.warning("DuplicateKeyError caught on user insert for email: %s", normalized_email)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists.",
        ) from exc
