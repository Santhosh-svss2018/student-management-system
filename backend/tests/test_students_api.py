"""
Tests for Student Management Module
Verifies Student CRUD endpoints, authorization rules, search, pagination, uniqueness constraints, and self-profile access.
"""

from bson import ObjectId
import pytest
from app.core.security import create_access_token, get_password_hash


@pytest.fixture
def admin_user(mock_db):
    user_doc = {
        "_id": ObjectId(),
        "full_name": "Admin Director",
        "email": "admin.director@edumanage.com",
        "hashed_password": get_password_hash("AdminSecret123!"),
        "role": "admin",
        "is_active": True,
    }
    mock_db.users.insert_one(user_doc)
    return user_doc


@pytest.fixture
def teacher_user(mock_db):
    user_doc = {
        "_id": ObjectId(),
        "full_name": "Faculty Professor",
        "email": "faculty.prof@edumanage.com",
        "hashed_password": get_password_hash("TeacherSecret123!"),
        "role": "teacher",
        "is_active": True,
    }
    mock_db.users.insert_one(user_doc)
    return user_doc


@pytest.fixture
def student_user(mock_db):
    user_doc = {
        "_id": ObjectId(),
        "full_name": "Student Alpha",
        "email": "alpha.student@edumanage.com",
        "hashed_password": get_password_hash("StudentSecret123!"),
        "role": "student",
        "is_active": True,
    }
    mock_db.users.insert_one(user_doc)
    return user_doc


@pytest.fixture
def other_student_user(mock_db):
    user_doc = {
        "_id": ObjectId(),
        "full_name": "Student Beta",
        "email": "beta.student@edumanage.com",
        "hashed_password": get_password_hash("StudentSecret123!"),
        "role": "student",
        "is_active": True,
    }
    mock_db.users.insert_one(user_doc)
    return user_doc


@pytest.fixture
def admin_headers(admin_user):
    token = create_access_token(subject=str(admin_user["_id"]), role="admin")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def teacher_headers(teacher_user):
    token = create_access_token(subject=str(teacher_user["_id"]), role="teacher")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def student_headers(student_user):
    token = create_access_token(subject=str(student_user["_id"]), role="student")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_student_headers(other_student_user):
    token = create_access_token(subject=str(other_student_user["_id"]), role="student")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_student_payload():
    return {
        "student_id": "STU-2024-001",
        "full_name": "Student Alpha",
        "email": "alpha.student@edumanage.com",
        "phone": "+1 (555) 123-4567",
        "date_of_birth": "2004-03-12",
        "gender": "female",
        "department": "Computer Science",
        "year": 3,
        "section": "A",
        "roll_number": "CS-2024-001",
        "address": "123 Campus Way",
        "is_active": True,
    }


# --- Creation Tests ---

def test_admin_creates_student_success(client, admin_headers, sample_student_payload):
    """Admin should successfully create a new student record (HTTP 201)."""
    response = client.post("/api/students/", json=sample_student_payload, headers=admin_headers)
    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert ObjectId.is_valid(data["id"])
    assert data["student_id"] == "STU-2024-001"
    assert data["full_name"] == "Student Alpha"
    assert data["email"] == "alpha.student@edumanage.com"
    assert data["department"] == "Computer Science"
    assert data["year"] == 3
    assert data["roll_number"] == "CS-2024-001"
    assert data["is_active"] is True
    assert "created_at" in data
    assert "updated_at" in data


def test_teacher_cannot_create_student(client, teacher_headers, sample_student_payload):
    """Teacher cannot create student (HTTP 403)."""
    response = client.post("/api/students/", json=sample_student_payload, headers=teacher_headers)
    assert response.status_code == 403


def test_student_cannot_create_student(client, student_headers, sample_student_payload):
    """Student cannot create student (HTTP 403)."""
    response = client.post("/api/students/", json=sample_student_payload, headers=student_headers)
    assert response.status_code == 403


# --- Duplicate Conflict Tests (HTTP 409) ---

def test_duplicate_student_id_returns_409(client, admin_headers, sample_student_payload):
    """Attempting to create student with already registered student_id returns 409."""
    res1 = client.post("/api/students/", json=sample_student_payload, headers=admin_headers)
    assert res1.status_code == 201

    duplicate_payload = {
        **sample_student_payload,
        "email": "different.email@edumanage.com",
        "roll_number": "DIFFERENT-ROLL-99",
    }
    res2 = client.post("/api/students/", json=duplicate_payload, headers=admin_headers)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"].lower()


def test_duplicate_email_returns_409(client, admin_headers, sample_student_payload):
    """Attempting to create student with duplicate email returns 409."""
    res1 = client.post("/api/students/", json=sample_student_payload, headers=admin_headers)
    assert res1.status_code == 201

    duplicate_payload = {
        **sample_student_payload,
        "student_id": "STU-DIFFERENT-99",
        "email": "   ALPHA.STUDENT@EDUMANAGE.COM   ",  # Normalized duplicate
        "roll_number": "DIFFERENT-ROLL-99",
    }
    res2 = client.post("/api/students/", json=duplicate_payload, headers=admin_headers)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"].lower()


def test_duplicate_roll_number_returns_409(client, admin_headers, sample_student_payload):
    """Attempting to create student with duplicate roll_number returns 409."""
    res1 = client.post("/api/students/", json=sample_student_payload, headers=admin_headers)
    assert res1.status_code == 201

    duplicate_payload = {
        **sample_student_payload,
        "student_id": "STU-DIFFERENT-99",
        "email": "different.email@edumanage.com",
    }
    res2 = client.post("/api/students/", json=duplicate_payload, headers=admin_headers)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"].lower()


# --- Retrieval Tests ---

def test_admin_and_teacher_get_student(client, admin_headers, teacher_headers, sample_student_payload):
    """Both Admin and Teacher should be able to get a student by student_id or _id."""
    create_res = client.post("/api/students/", json=sample_student_payload, headers=admin_headers)
    assert create_res.status_code == 201
    created_id = create_res.json()["id"]

    # Admin gets by student_id
    admin_get = client.get("/api/students/STU-2024-001", headers=admin_headers)
    assert admin_get.status_code == 200
    assert admin_get.json()["student_id"] == "STU-2024-001"

    # Teacher gets by database _id
    teacher_get = client.get(f"/api/students/{created_id}", headers=teacher_headers)
    assert teacher_get.status_code == 200
    assert teacher_get.json()["id"] == created_id


def test_student_cannot_access_another_student_record(client, student_headers, admin_headers, sample_student_payload):
    """Student cannot access individual student record by ID (HTTP 403)."""
    create_res = client.post("/api/students/", json=sample_student_payload, headers=admin_headers)
    assert create_res.status_code == 201

    response = client.get("/api/students/STU-2024-001", headers=student_headers)
    assert response.status_code == 403


# --- Student Self-Access (/api/students/me) ---

def test_student_can_access_own_profile(client, admin_headers, student_headers, other_student_headers, sample_student_payload):
    """Student accesses their own profile via GET /api/students/me."""
    # Create student record matching student_user email
    create_res = client.post("/api/students/", json=sample_student_payload, headers=admin_headers)
    assert create_res.status_code == 201

    # Student requests /me
    response = client.get("/api/students/me", headers=student_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "alpha.student@edumanage.com"
    assert data["student_id"] == "STU-2024-001"

    # Other student (whose student record doesn't exist yet) gets 404
    other_res = client.get("/api/students/me", headers=other_student_headers)
    assert other_res.status_code == 404


def test_non_student_cannot_access_student_me(client, teacher_headers):
    """Teacher calling /api/students/me receives HTTP 403 Forbidden."""
    response = client.get("/api/students/me", headers=teacher_headers)
    assert response.status_code == 403


# --- Update & Deactivate Tests ---

def test_admin_updates_student_success(client, admin_headers, sample_student_payload):
    """Admin successfully updates student record attributes."""
    client.post("/api/students/", json=sample_student_payload, headers=admin_headers)

    update_payload = {
        "full_name": "Student Alpha Updated",
        "year": 4,
        "phone": "+1 (555) 999-8888",
    }
    response = client.put("/api/students/STU-2024-001", json=update_payload, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Student Alpha Updated"
    assert data["year"] == 4
    assert data["phone"] == "+1 (555) 999-8888"


def test_teacher_cannot_update_student(client, admin_headers, teacher_headers, sample_student_payload):
    """Teacher cannot update student record (HTTP 403)."""
    client.post("/api/students/", json=sample_student_payload, headers=admin_headers)

    response = client.put("/api/students/STU-2024-001", json={"year": 4}, headers=teacher_headers)
    assert response.status_code == 403


def test_admin_deactivates_student(client, admin_headers, sample_student_payload):
    """Admin soft-deletes a student by marking is_active=False."""
    client.post("/api/students/", json=sample_student_payload, headers=admin_headers)

    delete_res = client.delete("/api/students/STU-2024-001", headers=admin_headers)
    assert delete_res.status_code == 200
    assert delete_res.json()["is_active"] is False

    # Confirm via retrieval that is_active is now False
    get_res = client.get("/api/students/STU-2024-001", headers=admin_headers)
    assert get_res.status_code == 200
    assert get_res.json()["is_active"] is False


# --- Search and Pagination Tests ---

def test_list_students_pagination_and_search(client, admin_headers):
    """Test pagination metadata and multi-field search filtering."""
    # Seed multiple student records
    for i in range(1, 6):
        client.post(
            "/api/students/",
            json={
                "student_id": f"STU-2024-{i:03d}",
                "full_name": f"Candidate {i} Person",
                "email": f"candidate{i}@edumanage.com",
                "department": "Mechanical" if i % 2 == 0 else "Electrical",
                "year": 2,
                "roll_number": f"ROLL-{i:03d}",
            },
            headers=admin_headers,
        )

    # Test Pagination (page=1, limit=2)
    p1_res = client.get("/api/students/?page=1&limit=2", headers=admin_headers)
    assert p1_res.status_code == 200
    p1_data = p1_res.json()
    assert len(p1_data["items"]) == 2
    assert p1_data["page"] == 1
    assert p1_data["limit"] == 2
    assert p1_data["total"] >= 5
    assert p1_data["pages"] >= 3

    # Test Search by roll number
    search_roll = client.get("/api/students/?search=ROLL-003", headers=admin_headers)
    assert search_roll.status_code == 200
    roll_data = search_roll.json()
    assert roll_data["total"] == 1
    assert roll_data["items"][0]["student_id"] == "STU-2024-003"

    # Test Search by department
    search_dept = client.get("/api/students/?search=Mechanical", headers=admin_headers)
    assert search_dept.status_code == 200
    assert search_dept.json()["total"] >= 2


# --- Unauthenticated & Not Found Tests ---

def test_unauthenticated_request_returns_401(client):
    """Requests without token return HTTP 401."""
    res_list = client.get("/api/students/")
    assert res_list.status_code == 401

    res_post = client.post("/api/students/", json={})
    assert res_post.status_code == 401


def test_missing_student_returns_404(client, admin_headers):
    """Looking up or modifying a non-existent student returns HTTP 404."""
    res_get = client.get("/api/students/NON-EXISTENT-ID", headers=admin_headers)
    assert res_get.status_code == 404

    res_put = client.put("/api/students/NON-EXISTENT-ID", json={"full_name": "Ghost"}, headers=admin_headers)
    assert res_put.status_code == 404

    res_del = client.delete("/api/students/NON-EXISTENT-ID", headers=admin_headers)
    assert res_del.status_code == 404
