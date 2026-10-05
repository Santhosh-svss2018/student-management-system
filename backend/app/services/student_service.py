"""
Student Service Module
Encapsulates business logic, database queries, search, pagination, and uniqueness validation for Student records.
"""

from datetime import datetime, timezone
import logging
import re
from typing import List, Optional, Tuple, Union
from bson import ObjectId
from fastapi import HTTPException, status
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from app.core.security import get_password_hash
from app.models.student import StudentCreate, StudentInDB, StudentUpdate
from app.models.user import UserRole

logger = logging.getLogger("edumanage.services.student")


def get_student_by_id(db: Database, id_or_object_id: Union[str, ObjectId]) -> Optional[StudentInDB]:
    """
    Finds a student record in MongoDB by its BSON ObjectId.
    """
    if isinstance(id_or_object_id, str):
        if not ObjectId.is_valid(id_or_object_id):
            return None
        object_id = ObjectId(id_or_object_id)
    else:
        object_id = id_or_object_id

    student_doc = db.students.find_one({"_id": object_id})
    if student_doc:
        return StudentInDB.model_validate(student_doc)
    return None


def get_student_by_student_id(db: Database, student_id: str) -> Optional[StudentInDB]:
    """
    Finds a student record in MongoDB by the institutional student_id.
    """
    student_doc = db.students.find_one({"student_id": student_id.strip()})
    if student_doc:
        return StudentInDB.model_validate(student_doc)
    return None


def get_student_by_email(db: Database, email: str) -> Optional[StudentInDB]:
    """
    Finds a student record in MongoDB by normalized email address.
    """
    normalized_email = email.strip().lower()
    student_doc = db.students.find_one({"email": normalized_email})
    if student_doc:
        return StudentInDB.model_validate(student_doc)
    return None


def get_student_by_identifier(db: Database, identifier: str) -> Optional[StudentInDB]:
    """
    Convenience lookup that checks student_id first, and falls back to BSON _id if valid.
    """
    trimmed = identifier.strip()
    student_doc = db.students.find_one({"student_id": trimmed})
    if not student_doc and ObjectId.is_valid(trimmed):
        student_doc = db.students.find_one({"_id": ObjectId(trimmed)})

    if student_doc:
        return StudentInDB.model_validate(student_doc)
    return None


def create_student(db: Database, student_in: StudentCreate) -> StudentInDB:
    """
    Creates and persists a new student document with uniqueness verification,
    and automatically creates/links a corresponding authentication user account
    in the users collection with Argon2 password hashing.
    """
    normalized_email = str(student_in.email).strip().lower()
    student_id = student_in.student_id.strip()
    roll_number = student_in.roll_number.strip()

    # Pre-check duplicates with specific conflict messages
    if db.students.find_one({"student_id": student_id}):
        logger.warning("Duplicate student creation attempt for student_id: %s", student_id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Student with ID '{student_id}' already exists.",
        )

    if db.students.find_one({"email": normalized_email}):
        logger.warning("Duplicate student creation attempt for email: %s", normalized_email)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Student with email '{normalized_email}' already exists.",
        )

    if db.students.find_one({"roll_number": roll_number}):
        logger.warning("Duplicate student creation attempt for roll_number: %s", roll_number)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Student with roll number '{roll_number}' already exists.",
        )

    # Check whether the email already belongs to a non-student user account
    existing_user = db.users.find_one({"email": normalized_email})
    if existing_user and existing_user.get("role") != UserRole.STUDENT.value:
        logger.warning("Email '%s' already belongs to a non-student user account.", normalized_email)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An account with email '{normalized_email}' already exists.",
        )

    now = datetime.now(timezone.utc)
    student_data = student_in.model_dump(exclude={"initial_password"})
    student_db = StudentInDB(
        **student_data,
        created_at=now,
        updated_at=now,
    )

    student_dict = student_db.model_dump(by_alias=True)

    try:
        db.students.insert_one(student_dict)
    except DuplicateKeyError as exc:
        logger.warning("DuplicateKeyError on student insert: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A student with this student_id, email, or roll number already exists.",
        ) from exc

    # Automatically create or link the user authentication account in users collection
    try:
        if existing_user:
            # Link existing student user account to this student_id
            db.users.update_one(
                {"_id": existing_user["_id"]},
                {
                    "$set": {
                        "student_id": student_id,
                        "full_name": student_in.full_name,
                        "updated_at": now,
                    }
                },
            )
            logger.info("Linked existing user '%s' to student_id: %s", normalized_email, student_id)
        else:
            initial_pwd = (
                student_in.initial_password.strip()
                if getattr(student_in, "initial_password", None) and student_in.initial_password.strip()
                else f"EduManage@{student_id}"
            )
            hashed_pwd = get_password_hash(initial_pwd)
            user_doc = {
                "full_name": student_in.full_name,
                "email": normalized_email,
                "hashed_password": hashed_pwd,
                "role": UserRole.STUDENT.value,
                "student_id": student_id,
                "is_active": student_in.is_active,
                "created_at": now,
                "updated_at": now,
            }
            db.users.insert_one(user_doc)
            logger.info("Created student user authentication account: %s (student_id: %s)", normalized_email, student_id)
    except Exception as exc:
        # Rollback student creation on user creation failure to maintain data consistency
        logger.error("Failed to create auth user for student %s. Rolling back student creation: %s", normalized_email, exc)
        db.students.delete_one({"_id": student_db.id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user authentication account: {str(exc)}",
        ) from exc

    logger.info("Successfully created student: %s (%s)", student_id, student_in.full_name)
    return student_db


def get_students(
    db: Database,
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
) -> Tuple[List[StudentInDB], int, int]:
    """
    Fetches paginated student records with multi-field regex search support.
    Returns (items, total_count, total_pages).
    """
    page_num = max(1, page)
    page_limit = min(max(1, limit), 100)
    skip = (page_num - 1) * page_limit

    filter_query = {}
    if search and search.strip():
        search_escaped = re.escape(search.strip())
        regex_pattern = {"$regex": search_escaped, "$options": "i"}
        filter_query["$or"] = [
            {"full_name": regex_pattern},
            {"email": regex_pattern},
            {"student_id": regex_pattern},
            {"roll_number": regex_pattern},
            {"department": regex_pattern},
        ]

    total = db.students.count_documents(filter_query)
    pages = (total + page_limit - 1) // page_limit if total > 0 else 0

    cursor = (
        db.students.find(filter_query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(page_limit)
    )

    items = [StudentInDB.model_validate(doc) for doc in cursor]
    return items, total, pages


def update_student(
    db: Database,
    identifier: str,
    student_update: StudentUpdate,
) -> Optional[StudentInDB]:
    """
    Updates specified fields of an existing student document and synchronizes
    full_name/email with the linked user authentication account.
    """
    existing = get_student_by_identifier(db, identifier)
    if not existing:
        return None

    update_dict = student_update.model_dump(exclude_unset=True)
    if not update_dict:
        return existing

    if "email" in update_dict and update_dict["email"] is not None:
        update_dict["email"] = str(update_dict["email"]).strip().lower()

    # Pre-check duplicate conflicts on updated fields
    if "student_id" in update_dict and update_dict["student_id"] != existing.student_id:
        if db.students.find_one({"student_id": update_dict["student_id"], "_id": {"$ne": existing.id}}):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Student with ID '{update_dict['student_id']}' already exists.",
            )

    if "email" in update_dict and update_dict["email"] != existing.email:
        if db.students.find_one({"email": update_dict["email"], "_id": {"$ne": existing.id}}):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Student with email '{update_dict['email']}' already exists.",
            )

    if "roll_number" in update_dict and update_dict["roll_number"] != existing.roll_number:
        if db.students.find_one({"roll_number": update_dict["roll_number"], "_id": {"$ne": existing.id}}):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Student with roll number '{update_dict['roll_number']}' already exists.",
            )

    now = datetime.now(timezone.utc)
    update_dict["updated_at"] = now

    try:
        db.students.update_one({"_id": existing.id}, {"$set": update_dict})
        updated_doc = db.students.find_one({"_id": existing.id})
        updated_student = StudentInDB.model_validate(updated_doc)

        # Synchronize user authentication record
        user_sync = {"updated_at": now}
        if "full_name" in update_dict:
            user_sync["full_name"] = updated_student.full_name
        if "email" in update_dict:
            user_sync["email"] = updated_student.email
        if "student_id" in update_dict:
            user_sync["student_id"] = updated_student.student_id

        db.users.update_one(
            {"$or": [{"student_id": existing.student_id}, {"email": existing.email}]},
            {"$set": user_sync},
        )

        return updated_student
    except DuplicateKeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A student with this student_id, email, or roll number already exists.",
        ) from exc


def deactivate_student(db: Database, identifier: str) -> Optional[StudentInDB]:
    """
    Soft-deletes a student record by setting is_active to False,
    and deactivates the corresponding user authentication account.
    """
    existing = get_student_by_identifier(db, identifier)
    if not existing:
        return None

    now = datetime.now(timezone.utc)
    db.students.update_one(
        {"_id": existing.id},
        {"$set": {"is_active": False, "updated_at": now}},
    )

    # Deactivate corresponding user account
    db.users.update_one(
        {"$or": [{"student_id": existing.student_id}, {"email": existing.email}]},
        {"$set": {"is_active": False, "updated_at": now}},
    )

    updated_doc = db.students.find_one({"_id": existing.id})
    return StudentInDB.model_validate(updated_doc)

