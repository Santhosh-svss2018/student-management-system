"""
Integration Tests for Phase 18: Admin User Account & Password Management
Tests automatic user account creation on student enrollment, Admin password reset,
Argon2 hashing verification, RBAC permissions (403 for students/teachers),
and login authentication flows.
"""

from bson import ObjectId
import pytest
from app.core.security import create_access_token, decode_access_token, get_password_hash, verify_password


@pytest.fixture
def admin_user(mock_db):
    user_doc = {
        "_id": ObjectId(),
        "full_name": "Dean Sarah Jenkins",
        "email": "sarah.jenkins@edumanage.edu",
        "hashed_password": get_password_hash("AdminSecret123!"),
        "role": "admin",
        "is_active": True,
    }
    mock_db.users.insert_one(user_doc)
    return user_doc


@pytest.fixture
def other_admin_user(mock_db):
    user_doc = {
        "_id": ObjectId(),
        "full_name": "Super Admin Roberts",
        "email": "roberts.admin@edumanage.edu",
        "hashed_password": get_password_hash("SuperAdmin123!"),
        "role": "admin",
        "is_active": True,
    }
    mock_db.users.insert_one(user_doc)
    return user_doc


@pytest.fixture
def teacher_user(mock_db):
    user_doc = {
        "_id": ObjectId(),
        "full_name": "Prof Marcus Vance",
        "email": "marcus.vance@edumanage.edu",
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
        "full_name": "Rahul Kumar",
        "email": "rahul.kumar@student.edumanage.edu",
        "hashed_password": get_password_hash("StudentInitial123!"),
        "role": "student",
        "student_id": "STU-2026-777",
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


# ==============================================================================
# 1. Automatic Student User Account Creation & Login Tests
# ==============================================================================

def test_admin_creates_student_automatically_creates_user_account(client, admin_headers, mock_db):
    """
    When an Admin registers a new student:
    1. Student document is inserted into students collection.
    2. Authentication user document is automatically created in users collection.
    3. Password is securely hashed with Argon2 (never plaintext).
    4. Student can immediately log in with the assigned password.
    """
    student_payload = {
        "student_id": "STU-2026-901",
        "full_name": "Priya Sharma",
        "email": "priya.sharma@edumanage.edu",
        "phone": "+1 (555) 987-6543",
        "department": "Computer Science",
        "year": 2,
        "section": "B",
        "roll_number": "CS-24-901",
        "is_active": True,
    }

    create_res = client.post("/api/students/", json=student_payload, headers=admin_headers)
    assert create_res.status_code == 201
    created_student = create_res.json()
    assert created_student["student_id"] == "STU-2026-901"
    assert created_student["email"] == "priya.sharma@edumanage.edu"

    # Verify user account in users collection
    user_doc = mock_db.users.find_one({"email": "priya.sharma@edumanage.edu"})
    assert user_doc is not None
    assert user_doc["full_name"] == "Priya Sharma"
    assert user_doc["role"] == "student"
    assert user_doc["student_id"] == "STU-2026-901"
    assert user_doc["is_active"] is True
    assert user_doc["hashed_password"].startswith("$argon2id$")

    # Default password is EduManage@STU-2026-901
    assert verify_password("EduManage@STU-2026-901", user_doc["hashed_password"]) is True

    # Test student login with default credentials
    login_res = client.post(
        "/api/auth/login",
        json={"email": "priya.sharma@edumanage.edu", "password": "EduManage@STU-2026-901"},
    )
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data

    # Verify token claims
    claims = decode_access_token(token_data["access_token"])
    assert claims["role"] == "student"
    assert claims["sub"] == str(user_doc["_id"])

    # Test student access to /api/students/me
    stu_headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    me_res = client.get("/api/students/me", headers=stu_headers)
    assert me_res.status_code == 200
    assert me_res.json()["student_id"] == "STU-2026-901"


def test_admin_creates_student_with_custom_initial_password(client, admin_headers, mock_db):
    """
    Admin can specify a custom initial_password when creating a student.
    The student can log in using that custom password.
    """
    student_payload = {
        "student_id": "STU-2026-902",
        "full_name": "Dev Patel",
        "email": "dev.patel@edumanage.edu",
        "department": "Information Technology",
        "year": 1,
        "roll_number": "IT-24-902",
        "initial_password": "CustomPassword99!",
        "is_active": True,
    }

    create_res = client.post("/api/students/", json=student_payload, headers=admin_headers)
    assert create_res.status_code == 201

    # Student document must NOT store initial_password
    stored_student = mock_db.students.find_one({"student_id": "STU-2026-902"})
    assert "initial_password" not in stored_student
    assert "password" not in stored_student
    assert "hashed_password" not in stored_student

    # Login with custom initial password succeeds
    login_res = client.post(
        "/api/auth/login",
        json={"email": "dev.patel@edumanage.edu", "password": "CustomPassword99!"},
    )
    assert login_res.status_code == 200


def test_admin_creates_student_duplicate_email_conflict_with_user(client, admin_headers, teacher_user):
    """
    Attempting to create a student with an email that already belongs to a non-student
    (e.g., teacher) returns HTTP 409 Conflict.
    """
    conflict_payload = {
        "student_id": "STU-2026-903",
        "full_name": "Duplicate Attempt",
        "email": teacher_user["email"],  # existing teacher email
        "department": "Computer Science",
        "year": 1,
        "roll_number": "CS-24-903",
    }
    res = client.post("/api/students/", json=conflict_payload, headers=admin_headers)
    assert res.status_code == 409
    assert "already exists" in res.json()["detail"].lower()


# ==============================================================================
# 2. Admin Password Management API Tests
# ==============================================================================

def test_admin_changes_student_password_success(client, admin_headers, student_user, mock_db):
    """
    Admin successfully changes a student's password:
    1. Returns HTTP 200 with success message.
    2. Does not expose password or hash in response.
    3. Updates Argon2 hash in users collection.
    4. Old password fails authentication.
    5. New password succeeds authentication.
    """
    student_id_str = str(student_user["_id"])
    payload = {"new_password": "BrandNewPassword2026!"}

    # Call PUT /api/users/{user_id}/password
    response = client.put(f"/api/users/{student_id_str}/password", json=payload, headers=admin_headers)
    assert response.status_code == 200
    res_data = response.json()
    assert "Password changed successfully" in res_data["message"]
    assert "hashed_password" not in res_data
    assert "password" not in res_data

    # Verify Argon2 hash in DB
    updated_user = mock_db.users.find_one({"_id": student_user["_id"]})
    assert verify_password("BrandNewPassword2026!", updated_user["hashed_password"]) is True
    assert verify_password("StudentInitial123!", updated_user["hashed_password"]) is False

    # Old password fails login (401)
    old_login = client.post(
        "/api/auth/login",
        json={"email": student_user["email"], "password": "StudentInitial123!"},
    )
    assert old_login.status_code == 401

    # New password succeeds login (200)
    new_login = client.post(
        "/api/auth/login",
        json={"email": student_user["email"], "password": "BrandNewPassword2026!"},
    )
    assert new_login.status_code == 200
    assert "access_token" in new_login.json()


def test_admin_changes_password_via_admin_prefix_route(client, admin_headers, student_user):
    """
    Admin can also use PUT /api/admin/users/{user_id}/password endpoint.
    """
    student_id_str = str(student_user["_id"])
    payload = {"new_password": "PrefixRoutePassword123!"}

    response = client.put(f"/api/admin/users/{student_id_str}/password", json=payload, headers=admin_headers)
    assert response.status_code == 200
    assert "Password changed successfully" in response.json()["message"]


def test_admin_changes_teacher_password_success(client, admin_headers, teacher_user, mock_db):
    """
    Admin successfully changes a Teacher/Faculty account's password.
    Teacher can immediately log in with the new password.
    """
    teacher_id_str = str(teacher_user["_id"])
    payload = {"new_password": "NewTeacherPassword2026!"}

    response = client.put(f"/api/users/{teacher_id_str}/password", json=payload, headers=admin_headers)
    assert response.status_code == 200

    # Old password fails
    old_login = client.post(
        "/api/auth/login",
        json={"email": teacher_user["email"], "password": "TeacherSecret123!"},
    )
    assert old_login.status_code == 401

    # New password succeeds
    new_login = client.post(
        "/api/auth/login",
        json={"email": teacher_user["email"], "password": "NewTeacherPassword2026!"},
    )
    assert new_login.status_code == 200
    claims = decode_access_token(new_login.json()["access_token"])
    assert claims["role"] == "teacher"


def test_admin_changes_password_by_student_id_or_email_lookup(client, admin_headers, student_user):
    """
    Password change API flexibly resolves student_id or email as the user identifier.
    """
    # Lookup by student_id
    res1 = client.put(
        f"/api/users/{student_user['student_id']}/password",
        json={"new_password": "PassViaStudentId123!"},
        headers=admin_headers,
    )
    assert res1.status_code == 200

    # Lookup by email
    res2 = client.put(
        f"/api/users/{student_user['email']}/password",
        json={"new_password": "PassViaEmailAddress123!"},
        headers=admin_headers,
    )
    assert res2.status_code == 200


# ==============================================================================
# 3. RBAC & Security Permission Enforcement Tests (403, 401, 404, 422)
# ==============================================================================

def test_student_cannot_change_password_forbidden(client, student_headers, student_user):
    """
    Student attempting to call password management endpoint receives HTTP 403 Forbidden.
    """
    response = client.put(
        f"/api/users/{student_user['_id']}/password",
        json={"new_password": "HackerPassword123!"},
        headers=student_headers,
    )
    assert response.status_code == 403
    assert "Forbidden" in response.json()["detail"]


def test_teacher_cannot_change_password_forbidden(client, teacher_headers, student_user):
    """
    Teacher attempting to call password management endpoint receives HTTP 403 Forbidden.
    """
    response = client.put(
        f"/api/users/{student_user['_id']}/password",
        json={"new_password": "TeacherTryingToChangePass123!"},
        headers=teacher_headers,
    )
    assert response.status_code == 403
    assert "Forbidden" in response.json()["detail"]


def test_unauthenticated_request_rejected(client, student_user):
    """
    Unauthenticated request receives HTTP 401 Unauthorized.
    """
    response = client.put(
        f"/api/users/{student_user['_id']}/password",
        json={"new_password": "NoAuthPassword123!"},
    )
    assert response.status_code == 401


def test_invalid_user_id_not_found(client, admin_headers):
    """
    Non-existent user identifier returns HTTP 404 Not Found.
    """
    fake_id = str(ObjectId())
    response = client.put(
        f"/api/users/{fake_id}/password",
        json={"new_password": "ValidPassword123!"},
        headers=admin_headers,
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_weak_or_short_password_rejected(client, admin_headers, student_user):
    """
    Password shorter than 8 characters is rejected with HTTP 422 Unprocessable Entity.
    """
    student_id_str = str(student_user["_id"])

    # Too short
    res_short = client.put(
        f"/api/users/{student_id_str}/password",
        json={"new_password": "short"},
        headers=admin_headers,
    )
    assert res_short.status_code == 422

    # Empty string
    res_empty = client.put(
        f"/api/users/{student_id_str}/password",
        json={"new_password": "   "},
        headers=admin_headers,
    )
    assert res_empty.status_code == 422


def test_admin_cannot_change_another_admin_password(client, admin_headers, other_admin_user):
    """
    An Admin cannot change another Admin's password (HTTP 403 Forbidden).
    """
    other_admin_id = str(other_admin_user["_id"])
    response = client.put(
        f"/api/users/{other_admin_id}/password",
        json={"new_password": "AdminTakeover123!"},
        headers=admin_headers,
    )
    assert response.status_code == 403
    assert "another administrator" in response.json()["detail"].lower()


def test_admin_sets_password_for_student_without_prior_user_account(client, admin_headers, mock_db):
    """
    If a student record exists in students collection (e.g. from an earlier seed or DB state)
    without an existing user auth account in users collection:
    Admin calling change_password automatically provisions the user account on-demand
    with the new password and allows instant student login.
    """
    # Insert student record directly into students collection without a users collection account
    student_obj_id = ObjectId()
    mock_db.students.insert_one({
        "_id": student_obj_id,
        "student_id": "STU-LEGACY-001",
        "full_name": "Legacy Student",
        "email": "legacy.student@edumanage.edu",
        "roll_number": "CS-20-001",
        "department": "Computer Science",
        "year": 4,
        "is_active": True,
    })

    # Verify no account exists in users collection before password set
    assert mock_db.users.find_one({"email": "legacy.student@edumanage.edu"}) is None

    # Admin sets password using the student's BSON _id
    response = client.put(
        f"/api/users/{str(student_obj_id)}/password",
        json={"new_password": "NewlyProvisionedPass123!"},
        headers=admin_headers,
    )
    assert response.status_code == 200

    # Verify user account was created in users collection
    user_doc = mock_db.users.find_one({"email": "legacy.student@edumanage.edu"})
    assert user_doc is not None
    assert user_doc["role"] == "student"
    assert user_doc["student_id"] == "STU-LEGACY-001"
    assert verify_password("NewlyProvisionedPass123!", user_doc["hashed_password"]) is True

    # Student can immediately log in
    login_res = client.post(
        "/api/auth/login",
        json={"email": "legacy.student@edumanage.edu", "password": "NewlyProvisionedPass123!"},
    )
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()

