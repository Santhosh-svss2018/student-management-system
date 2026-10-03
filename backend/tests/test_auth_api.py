"""
Authentication & JWT Tests
Verifies login endpoint, credential validation, token generation, and get_current_user dependency.
"""

from datetime import timedelta
from bson import ObjectId
import jwt
import pytest

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash


@pytest.fixture
def active_student(mock_db):
    """Creates an active student user in the mock database."""
    user_doc = {
        "_id": ObjectId(),
        "full_name": "Active Student",
        "email": "active.student@edumanage.com",
        "hashed_password": get_password_hash("StudentSecret123!"),
        "role": "student",
        "is_active": True,
    }
    mock_db.users.insert_one(user_doc)
    return user_doc


@pytest.fixture
def inactive_teacher(mock_db):
    """Creates an inactive teacher user in the mock database."""
    user_doc = {
        "_id": ObjectId(),
        "full_name": "Inactive Teacher",
        "email": "inactive.teacher@edumanage.com",
        "hashed_password": get_password_hash("TeacherSecret123!"),
        "role": "teacher",
        "is_active": False,
    }
    mock_db.users.insert_one(user_doc)
    return user_doc


def test_login_success(client, active_student):
    """Test successful login returns access_token and bearer token_type."""
    payload = {
        "email": "active.student@edumanage.com",
        "password": "StudentSecret123!",
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"].lower() == "bearer"

    # Decode and verify JWT token claims
    token = data["access_token"]
    decoded = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    assert decoded["sub"] == str(active_student["_id"])
    assert decoded["role"] == "student"
    assert "exp" in decoded


def test_login_email_normalization(client, active_student):
    """Test login succeeds when email has mixed casing and surrounding whitespace."""
    payload = {
        "email": "   ACTIVE.STUDENT@EDUMANAGE.COM   ",
        "password": "StudentSecret123!",
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client, active_student):
    """Test login with wrong password returns HTTP 401."""
    payload = {
        "email": "active.student@edumanage.com",
        "password": "WrongPassword999!",
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401
    assert "invalid email or password" in response.json()["detail"].lower()
    assert response.headers.get("www-authenticate") == "Bearer"


def test_login_unknown_email(client):
    """Test login with non-existent email returns HTTP 401."""
    payload = {
        "email": "nonexistent.user@edumanage.com",
        "password": "SomePassword123!",
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401
    assert "invalid email or password" in response.json()["detail"].lower()


def test_login_inactive_user(client, inactive_teacher):
    """Test login with an inactive account returns HTTP 401."""
    payload = {
        "email": "inactive.teacher@edumanage.com",
        "password": "TeacherSecret123!",
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401
    assert "inactive" in response.json()["detail"].lower()


def test_get_current_user_valid_jwt(client, active_student):
    """Test accessing protected /api/auth/me with valid Bearer token."""
    token = create_access_token(
        subject=str(active_student["_id"]),
        role="student",
    )
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == str(active_student["_id"])
    assert data["email"] == active_student["email"]
    assert data["role"] == "student"
    assert "hashed_password" not in data


def test_get_current_user_invalid_jwt(client):
    """Test accessing protected route with malformed/invalid token returns HTTP 401."""
    headers = {"Authorization": "Bearer invalid.garbage.token"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 401
    assert "invalid token" in response.json()["detail"].lower()


def test_get_current_user_expired_jwt(client, active_student):
    """Test accessing protected route with expired token returns HTTP 401."""
    expired_token = create_access_token(
        subject=str(active_student["_id"]),
        role="student",
        expires_delta=timedelta(seconds=-10),  # In the past
    )
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()


def test_get_current_user_missing_auth_header(client):
    """Test accessing protected route without Authorization header returns HTTP 401."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    assert "missing authorization header" in response.json()["detail"].lower()


def test_get_current_user_inactive_user(client, inactive_teacher):
    """Test accessing protected route when the token owner is inactive returns HTTP 401."""
    token = create_access_token(
        subject=str(inactive_teacher["_id"]),
        role="teacher",
    )
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 401
    assert "inactive" in response.json()["detail"].lower()


def test_get_current_user_user_not_found(client):
    """Test accessing protected route with valid token but non-existent user ID returns HTTP 401."""
    non_existent_id = str(ObjectId())
    token = create_access_token(
        subject=non_existent_id,
        role="admin",
    )
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 401
    assert "not found" in response.json()["detail"].lower()
