"""
Tests for User Models and Pydantic v2 Schemas
Verifies data validation, normalization, and serialization rules.
"""

import pytest
from datetime import datetime, timezone
from bson import ObjectId
from pydantic import ValidationError

from app.models.user import (
    UserRole,
    UserCreate,
    UserInDB,
    UserResponse,
    PyObjectId,
)


def test_user_create_valid():
    """Test valid UserCreate schema creation and default values."""
    user = UserCreate(
        full_name="Jane Doe",
        email="jane.doe@example.com",
        password="ValidPassword123!",
    )
    assert user.full_name == "Jane Doe"
    assert user.email == "jane.doe@example.com"
    assert user.role == UserRole.STUDENT
    assert user.is_active is True
    assert user.password == "ValidPassword123!"


def test_user_create_email_normalization():
    """Test that email addresses are lowercased and stripped of outer whitespace."""
    user = UserCreate(
        full_name="Jane Doe",
        email="  JANE.DOE@ExAmPlE.CoM   ",
        password="ValidPassword123!",
    )
    assert user.email == "jane.doe@example.com"


def test_user_create_invalid_email():
    """Test that malformed email addresses are rejected."""
    with pytest.raises(ValidationError):
        UserCreate(
            full_name="Jane Doe",
            email="not-a-valid-email",
            password="ValidPassword123!",
        )


def test_user_create_short_password():
    """Test that passwords shorter than 8 characters are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            full_name="Jane Doe",
            email="jane.doe@example.com",
            password="short",
        )
    assert "at least 8 characters" in str(exc_info.value) or "min_length" in str(exc_info.value) or "8" in str(exc_info.value)


def test_user_create_empty_name():
    """Test that whitespace-only names are rejected."""
    with pytest.raises(ValidationError):
        UserCreate(
            full_name="   ",
            email="jane.doe@example.com",
            password="ValidPassword123!",
        )


def test_user_role_enum_validation():
    """Test allowed and disallowed user roles."""
    admin_user = UserCreate(
        full_name="Admin Person",
        email="admin@example.com",
        password="AdminPassword123!",
        role=UserRole.ADMIN,
    )
    assert admin_user.role == UserRole.ADMIN

    teacher_user = UserCreate(
        full_name="Teacher Person",
        email="teacher@example.com",
        password="TeacherPassword123!",
        role=UserRole.TEACHER,
    )
    assert teacher_user.role == UserRole.TEACHER

    with pytest.raises(ValidationError):
        UserCreate(
            full_name="Invalid Role Person",
            email="invalid@example.com",
            password="Password123!",
            role="superhero",  # Invalid role
        )


def test_user_in_db_model():
    """Test UserInDB document structure and ObjectId default."""
    oid = ObjectId()
    now = datetime.now(timezone.utc)
    user_db = UserInDB(
        _id=oid,
        full_name="DB User",
        email="dbuser@example.com",
        hashed_password="$argon2id$mockhashvalue",
        role=UserRole.STUDENT,
        is_active=True,
        created_at=now,
    )
    assert user_db.id == oid
    assert user_db.hashed_password == "$argon2id$mockhashvalue"

    dumped = user_db.model_dump(by_alias=True)
    assert dumped["_id"] == oid
    assert "hashed_password" in dumped


def test_user_response_omits_hashed_password():
    """Test that UserResponse safely excludes hashed_password and serializes ObjectId."""
    oid = ObjectId()
    now = datetime.now(timezone.utc)
    user_data = {
        "_id": oid,
        "full_name": "Public User",
        "email": "public@example.com",
        "hashed_password": "$argon2id$secret_should_never_leak",
        "role": "student",
        "is_active": True,
        "created_at": now,
    }

    response_model = UserResponse.model_validate(user_data)
    json_data = response_model.model_dump(mode="json")

    assert json_data["id"] == str(oid)
    assert json_data["email"] == "public@example.com"
    assert json_data["role"] == "student"
    assert "hashed_password" not in json_data
    assert "password" not in json_data
