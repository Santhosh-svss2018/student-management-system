"""
Tests for Role-Based Access Control (RBAC)
Verifies endpoint permissions for Admin, Teacher, and Student roles, and ensures proper 403/401 HTTP codes.
"""

from bson import ObjectId
import pytest
from app.core.security import create_access_token, get_password_hash


@pytest.fixture
def test_admin_user(mock_db):
    """Creates an active admin user in the mock database."""
    user_doc = {
        "_id": ObjectId(),
        "full_name": "System Admin",
        "email": "admin@edumanage.com",
        "hashed_password": get_password_hash("AdminSecret123!"),
        "role": "admin",
        "is_active": True,
    }
    mock_db.users.insert_one(user_doc)
    return user_doc


@pytest.fixture
def test_teacher_user(mock_db):
    """Creates an active teacher user in the mock database."""
    user_doc = {
        "_id": ObjectId(),
        "full_name": "Math Teacher",
        "email": "teacher@edumanage.com",
        "hashed_password": get_password_hash("TeacherSecret123!"),
        "role": "teacher",
        "is_active": True,
    }
    mock_db.users.insert_one(user_doc)
    return user_doc


@pytest.fixture
def test_student_user(mock_db):
    """Creates an active student user in the mock database."""
    user_doc = {
        "_id": ObjectId(),
        "full_name": "CS Student",
        "email": "student@edumanage.com",
        "hashed_password": get_password_hash("StudentSecret123!"),
        "role": "student",
        "is_active": True,
    }
    mock_db.users.insert_one(user_doc)
    return user_doc


@pytest.fixture
def admin_headers(test_admin_user):
    token = create_access_token(subject=str(test_admin_user["_id"]), role="admin")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def teacher_headers(test_teacher_user):
    token = create_access_token(subject=str(test_teacher_user["_id"]), role="teacher")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def student_headers(test_student_user):
    token = create_access_token(subject=str(test_student_user["_id"]), role="student")
    return {"Authorization": f"Bearer {token}"}


# --- Admin Endpoint Tests (/api/test/admin) ---

def test_admin_can_access_admin_endpoint(client, admin_headers):
    """Admin user should successfully access the admin-only endpoint."""
    response = client.get("/api/test/admin", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "admin" in data["message"].lower()
    assert data["role"] == "admin"


def test_teacher_cannot_access_admin_endpoint(client, teacher_headers):
    """Teacher user should be forbidden (403) from accessing admin endpoint."""
    response = client.get("/api/test/admin", headers=teacher_headers)
    assert response.status_code == 403
    assert "admin access required" in response.json()["detail"].lower()


def test_student_cannot_access_admin_endpoint(client, student_headers):
    """Student user should be forbidden (403) from accessing admin endpoint."""
    response = client.get("/api/test/admin", headers=student_headers)
    assert response.status_code == 403
    assert "admin access required" in response.json()["detail"].lower()


# --- Teacher Endpoint Tests (/api/test/teacher) ---

def test_admin_can_access_teacher_endpoint(client, admin_headers):
    """Admin user should successfully access teacher/admin endpoint."""
    response = client.get("/api/test/teacher", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "admin"


def test_teacher_can_access_teacher_endpoint(client, teacher_headers):
    """Teacher user should successfully access teacher/admin endpoint."""
    response = client.get("/api/test/teacher", headers=teacher_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "teacher"


def test_student_cannot_access_teacher_endpoint(client, student_headers):
    """Student user should be forbidden (403) from accessing teacher/admin endpoint."""
    response = client.get("/api/test/teacher", headers=student_headers)
    assert response.status_code == 403
    assert "teacher or admin access required" in response.json()["detail"].lower()


# --- Student Endpoint Tests (/api/test/student) ---

def test_student_can_access_student_endpoint(client, student_headers):
    """Student user should successfully access student-only endpoint."""
    response = client.get("/api/test/student", headers=student_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "student"


def test_admin_cannot_access_student_only_endpoint(client, admin_headers):
    """Admin user should be forbidden (403) from accessing student-only endpoint."""
    response = client.get("/api/test/student", headers=admin_headers)
    assert response.status_code == 403
    assert "student access required" in response.json()["detail"].lower()


def test_teacher_cannot_access_student_only_endpoint(client, teacher_headers):
    """Teacher user should be forbidden (403) from accessing student-only endpoint."""
    response = client.get("/api/test/student", headers=teacher_headers)
    assert response.status_code == 403
    assert "student access required" in response.json()["detail"].lower()


# --- Authenticated Endpoint Tests (/api/test/authenticated) ---

def test_student_can_access_authenticated_endpoint(client, student_headers):
    """Student user can access general authenticated endpoint."""
    response = client.get("/api/test/authenticated", headers=student_headers)
    assert response.status_code == 200
    assert response.json()["role"] == "student"


def test_teacher_can_access_authenticated_endpoint(client, teacher_headers):
    """Teacher user can access general authenticated endpoint."""
    response = client.get("/api/test/authenticated", headers=teacher_headers)
    assert response.status_code == 200
    assert response.json()["role"] == "teacher"


def test_admin_can_access_authenticated_endpoint(client, admin_headers):
    """Admin user can access general authenticated endpoint."""
    response = client.get("/api/test/authenticated", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["role"] == "admin"


# --- Unauthenticated and Malformed Token Tests ---

def test_unauthenticated_request_returns_401(client):
    """Unauthenticated request to RBAC endpoint returns HTTP 401."""
    response = client.get("/api/test/authenticated")
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"


def test_invalid_jwt_returns_401(client):
    """Request with invalid JWT returns HTTP 401."""
    headers = {"Authorization": "Bearer invalid.jwt.payload"}
    response = client.get("/api/test/authenticated", headers=headers)
    assert response.status_code == 401
    assert "invalid token" in response.json()["detail"].lower()
