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


def find_user_by_any_identifier(db: Database, identifier: str) -> Optional[UserInDB]:
    """
    Finds a user document across multiple possible identifiers:
    1. BSON ObjectId in users collection (_id)
    2. Email in users collection
    3. student_id in users collection
    4. student_id in students collection -> linked user email
    5. BSON ObjectId in students collection -> linked user email
    """
    if not identifier or not isinstance(identifier, str):
        return None

    trimmed = identifier.strip()
    if not trimmed:
        return None

    # 1. Check user _id if valid ObjectId
    if ObjectId.is_valid(trimmed):
        user_doc = db.users.find_one({"_id": ObjectId(trimmed)})
        if user_doc:
            return UserInDB.model_validate(user_doc)

    # 2. Check user email
    normalized_email = trimmed.lower()
    user_doc = db.users.find_one({"email": normalized_email})
    if user_doc:
        return UserInDB.model_validate(user_doc)

    # 3. Check student_id field in users collection
    user_doc = db.users.find_one({"student_id": trimmed})
    if user_doc:
        return UserInDB.model_validate(user_doc)

    # 4. Check students collection by student_id
    student_doc = db.students.find_one({"student_id": trimmed})
    if student_doc and student_doc.get("email"):
        student_email = str(student_doc["email"]).strip().lower()
        user_doc = db.users.find_one({"email": student_email})
        if user_doc:
            return UserInDB.model_validate(user_doc)

    # 5. Check students collection by _id
    if ObjectId.is_valid(trimmed):
        student_doc = db.students.find_one({"_id": ObjectId(trimmed)})
        if student_doc and student_doc.get("email"):
            student_email = str(student_doc["email"]).strip().lower()
            user_doc = db.users.find_one({"email": student_email})
            if user_doc:
                return UserInDB.model_validate(user_doc)

    return None


def change_user_password(
    db: Database,
    user_identifier: str,
    new_password: str,
    current_admin: UserInDB,
) -> UserInDB:
    """
    Admin-only operation to change another user's password.
    - Validates new password rules.
    - Ensures only Admin can perform the update.
    - Restricts changing other Admin account passwords unless self.
    - If user exists in users collection: hashes password with Argon2 and updates it.
    - If user does not exist in users collection but exists in students collection:
      automatically creates the missing user auth account on-the-fly with the new password.
    - Returns updated user model.
    """
    from datetime import datetime, timezone
    from app.models.user import UserRole

    # Validate password
    if not new_password or not isinstance(new_password, str):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password cannot be empty.",
        )

    clean_password = new_password.strip()
    if len(clean_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters long.",
        )

    # Verify acting admin role
    admin_role = current_admin.role.value if hasattr(current_admin.role, "value") else str(current_admin.role)
    if admin_role != UserRole.ADMIN.value:
        logger.warning("Unauthorized password change attempt by user '%s' (role: %s)", current_admin.email, admin_role)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Only administrators can manage passwords.",
        )

    # Find target user in users collection
    target_user = find_user_by_any_identifier(db, user_identifier)
    now = datetime.now(timezone.utc)
    hashed_password = get_password_hash(new_password)

    if not target_user:
        # Check if user_identifier belongs to an existing student in students collection
        # who does not have an authentication account in users collection yet
        student_doc = None
        trimmed = user_identifier.strip()
        if ObjectId.is_valid(trimmed):
            student_doc = db.students.find_one({"_id": ObjectId(trimmed)})
        if not student_doc:
            student_doc = db.students.find_one({"student_id": trimmed})
        if not student_doc:
            student_doc = db.students.find_one({"email": trimmed.lower()})

        if student_doc:
            # On-demand provisioning of user auth account for student record
            student_email = str(student_doc["email"]).strip().lower()
            student_id = str(student_doc.get("student_id", trimmed)).strip()
            full_name = student_doc.get("full_name", "Student")
            is_active = student_doc.get("is_active", True)

            user_doc = {
                "full_name": full_name,
                "email": student_email,
                "hashed_password": hashed_password,
                "role": UserRole.STUDENT.value,
                "student_id": student_id,
                "is_active": is_active,
                "created_at": now,
                "updated_at": now,
            }
            db.users.insert_one(user_doc)
            logger.info("Created user auth account on password change for student: %s (%s)", student_email, student_id)
            target_user = UserInDB.model_validate(user_doc)
            return target_user
        else:
            logger.warning("Password change failed: User identifier '%s' not found.", user_identifier)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with identifier '{user_identifier}' was not found.",
            )

    # Verify target role policy: Cannot change another admin's password
    target_role = target_user.role.value if hasattr(target_user.role, "value") else str(target_user.role)
    if target_role == UserRole.ADMIN.value and str(target_user.id) != str(current_admin.id):
        logger.warning(
            "Admin '%s' attempted to change password for another admin '%s'",
            current_admin.email,
            target_user.email,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot change password for another administrator account.",
        )

    # Update existing user's password in users collection
    db.users.update_one(
        {"_id": target_user.id},
        {"$set": {"hashed_password": hashed_password, "updated_at": now}},
    )

    logger.info(
        "Admin '%s' successfully changed password for user '%s' (role: %s, ID: %s)",
        current_admin.email,
        target_user.email,
        target_role,
        target_user.id,
    )

    updated_doc = db.users.find_one({"_id": target_user.id})
    return UserInDB.model_validate(updated_doc)


