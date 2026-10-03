"""
Integration Tests for Users API Endpoints and Database Persistence
Verifies HTTP endpoints, status codes, password hashing in DB, and duplicate handling.
"""

from bson import ObjectId
from app.core.security import verify_password


def test_create_user_success(client, mock_db):
    """Test successful user creation via POST /api/users/."""
    payload = {
        "full_name": "Test Student",
        "email": "Student.One@EduManage.com",
        "password": "SecurePassword123!",
        "role": "student",
    }
    response = client.post("/api/users/", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert ObjectId.is_valid(data["id"])
    assert data["full_name"] == "Test Student"
    assert data["email"] == "student.one@edumanage.com"
    assert data["role"] == "student"
    assert data["is_active"] is True
    assert "created_at" in data

    # Verify sensitive fields are NOT exposed
    assert "hashed_password" not in data
    assert "password" not in data

    # Verify directly in the database that password was hashed
    stored_user = mock_db.users.find_one({"email": "student.one@edumanage.com"})
    assert stored_user is not None
    assert stored_user["hashed_password"] != "SecurePassword123!"
    assert stored_user["hashed_password"].startswith("$argon2id$")
    assert verify_password("SecurePassword123!", stored_user["hashed_password"]) is True


def test_create_user_duplicate_email_conflict(client):
    """Test that attempting to register an existing email returns HTTP 409."""
    payload = {
        "full_name": "First Teacher",
        "email": "teacher@edumanage.com",
        "password": "TeacherPassword123!",
        "role": "teacher",
    }
    # First creation
    res1 = client.post("/api/users/", json=payload)
    assert res1.status_code == 201

    # Duplicate creation with same email
    res2 = client.post("/api/users/", json=payload)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"].lower()


def test_create_user_duplicate_email_case_insensitive(client):
    """Test duplicate detection across different casing and whitespace."""
    payload1 = {
        "full_name": "Admin User",
        "email": "admin@edumanage.com",
        "password": "AdminPassword123!",
        "role": "admin",
    }
    res1 = client.post("/api/users/", json=payload1)
    assert res1.status_code == 201

    payload2 = {
        "full_name": "Admin Clone",
        "email": "  ADMIN@EDUMANAGE.COM  ",
        "password": "DifferentPassword123!",
        "role": "admin",
    }
    res2 = client.post("/api/users/", json=payload2)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"].lower()


def test_create_user_validation_error_short_password(client):
    """Test validation rejection when password is under 8 characters."""
    payload = {
        "full_name": "Invalid User",
        "email": "invalid@edumanage.com",
        "password": "123",  # Under 8 chars
        "role": "student",
    }
    response = client.post("/api/users/", json=payload)
    assert response.status_code == 422


def test_get_user_by_id_success(client):
    """Test retrieving an existing user profile by ID."""
    create_payload = {
        "full_name": "Queryable User",
        "email": "query@edumanage.com",
        "password": "QueryPassword123!",
        "role": "teacher",
    }
    create_res = client.post("/api/users/", json=create_payload)
    assert create_res.status_code == 201
    user_id = create_res.json()["id"]

    get_res = client.get(f"/api/users/{user_id}")
    assert get_res.status_code == 200
    user_data = get_res.json()
    assert user_data["id"] == user_id
    assert user_data["email"] == "query@edumanage.com"
    assert user_data["role"] == "teacher"
    assert "hashed_password" not in user_data


def test_get_user_by_id_not_found(client):
    """Test 404 response when user ID does not exist."""
    fake_id = str(ObjectId())
    response = client.get(f"/api/users/{fake_id}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_user_by_invalid_objectid(client):
    """Test 404 response for malformed ObjectId string."""
    response = client.get("/api/users/not-a-valid-id")
    assert response.status_code == 404


def test_list_users(client):
    """Test listing users with pagination."""
    # Create multiple users
    for i in range(3):
        client.post(
            "/api/users/",
            json={
                "full_name": f"User {i}",
                "email": f"user{i}@edumanage.com",
                "password": "Password123!",
                "role": "student",
            },
        )

    response = client.get("/api/users/?skip=0&limit=10")
    assert response.status_code == 200
    users = response.json()
    assert len(users) >= 3
    for u in users:
        assert "id" in u
        assert "email" in u
        assert "hashed_password" not in u


def test_existing_health_endpoints(client):
    """Verify that existing health and metadata endpoints continue functioning."""
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert "users" in res_root.json()

    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "success"
