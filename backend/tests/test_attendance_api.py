"""
Tests for Attendance Management Module
Verifies Attendance CRUD endpoints, authorization rules (Admin, Teacher, Student),
date-range filtering, summary calculations, duplicate uniqueness constraints, and student self-access.
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
def sample_student(mock_db):
    """Seed a valid student record in MongoDB."""
    student_doc = {
        "_id": ObjectId(),
        "student_id": "STU-2024-001",
        "full_name": "Student Alpha",
        "email": "alpha.student@edumanage.com",
        "department": "Computer Science",
        "year": 3,
        "roll_number": "CS-2024-001",
        "is_active": True,
    }
    mock_db.students.insert_one(student_doc)
    return student_doc


@pytest.fixture
def sample_student_beta(mock_db):
    """Seed second valid student record in MongoDB."""
    student_doc = {
        "_id": ObjectId(),
        "student_id": "STU-2024-002",
        "full_name": "Student Beta",
        "email": "beta.student@edumanage.com",
        "department": "Information Technology",
        "year": 2,
        "roll_number": "IT-2024-002",
        "is_active": True,
    }
    mock_db.students.insert_one(student_doc)
    return student_doc


# ==============================================================================
# 1. Authentication & Security Tests
# ==============================================================================

def test_unauthenticated_request_returns_401(client):
    """Unauthenticated requests return HTTP 401."""
    res_get = client.get("/api/attendance/")
    assert res_get.status_code == 401

    res_post = client.post("/api/attendance/", json={})
    assert res_post.status_code == 401

    res_me = client.get("/api/attendance/me")
    assert res_me.status_code == 401


def test_invalid_token_returns_401(client):
    """Requests with invalid JWT return HTTP 401."""
    bad_headers = {"Authorization": "Bearer invalid.jwt.token"}
    res = client.get("/api/attendance/", headers=bad_headers)
    assert res.status_code == 401


# ==============================================================================
# 2. Authorization Rules (Admin, Teacher, Student)
# ==============================================================================

def test_admin_can_create_attendance(client, admin_headers, sample_student):
    """Admin can record attendance (HTTP 201)."""
    payload = {
        "student_id": sample_student["student_id"],
        "date": "2026-10-01",
        "status": "present",
        "remarks": "On time",
    }
    res = client.post("/api/attendance/", json=payload, headers=admin_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["student_id"] == sample_student["student_id"]
    assert data["status"] == "present"
    assert data["marked_by"] == "admin.director@edumanage.com"


def test_teacher_can_create_attendance(client, teacher_headers, sample_student):
    """Teacher can record attendance (HTTP 201)."""
    payload = {
        "student_id": sample_student["student_id"],
        "date": "2026-10-02",
        "status": "late",
        "remarks": "10 mins late",
    }
    res = client.post("/api/attendance/", json=payload, headers=teacher_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["student_id"] == sample_student["student_id"]
    assert data["status"] == "late"
    assert data["marked_by"] == "faculty.prof@edumanage.com"


def test_student_cannot_create_attendance(client, student_headers, sample_student):
    """Student is forbidden from recording attendance (HTTP 403)."""
    payload = {
        "student_id": sample_student["student_id"],
        "date": "2026-10-03",
        "status": "present",
    }
    res = client.post("/api/attendance/", json=payload, headers=student_headers)
    assert res.status_code == 403


def test_admin_and_teacher_can_update_attendance(client, admin_headers, teacher_headers, sample_student):
    """Both Admin and Teacher can update attendance records."""
    # Create by admin
    create_res = client.post(
        "/api/attendance/",
        json={"student_id": sample_student["student_id"], "date": "2026-10-01", "status": "absent"},
        headers=admin_headers,
    )
    assert create_res.status_code == 201
    att_id = create_res.json()["attendance_id"]

    # Teacher updates to present
    update_res = client.put(
        f"/api/attendance/{att_id}",
        json={"status": "present", "remarks": "Status updated by faculty"},
        headers=teacher_headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "present"
    assert update_res.json()["remarks"] == "Status updated by faculty"

    # Admin updates to excused
    admin_update = client.put(
        f"/api/attendance/{att_id}",
        json={"status": "excused"},
        headers=admin_headers,
    )
    assert admin_update.status_code == 200
    assert admin_update.json()["status"] == "excused"


def test_student_cannot_update_attendance(client, admin_headers, student_headers, sample_student):
    """Student cannot modify attendance records (HTTP 403)."""
    create_res = client.post(
        "/api/attendance/",
        json={"student_id": sample_student["student_id"], "date": "2026-10-01", "status": "absent"},
        headers=admin_headers,
    )
    att_id = create_res.json()["attendance_id"]

    res = client.put(f"/api/attendance/{att_id}", json={"status": "present"}, headers=student_headers)
    assert res.status_code == 403


def test_admin_can_delete_attendance(client, admin_headers, sample_student):
    """Admin can delete attendance record (HTTP 200)."""
    create_res = client.post(
        "/api/attendance/",
        json={"student_id": sample_student["student_id"], "date": "2026-10-01", "status": "absent"},
        headers=admin_headers,
    )
    att_id = create_res.json()["attendance_id"]

    delete_res = client.delete(f"/api/attendance/{att_id}", headers=admin_headers)
    assert delete_res.status_code == 200

    # Ensure it's deleted
    get_res = client.get(f"/api/attendance/{att_id}", headers=admin_headers)
    assert get_res.status_code == 404


def test_teacher_cannot_delete_attendance(client, admin_headers, teacher_headers, sample_student):
    """Teacher cannot delete attendance records (HTTP 403)."""
    create_res = client.post(
        "/api/attendance/",
        json={"student_id": sample_student["student_id"], "date": "2026-10-01", "status": "absent"},
        headers=admin_headers,
    )
    att_id = create_res.json()["attendance_id"]

    res = client.delete(f"/api/attendance/{att_id}", headers=teacher_headers)
    assert res.status_code == 403


def test_student_cannot_delete_attendance(client, admin_headers, student_headers, sample_student):
    """Student cannot delete attendance records (HTTP 403)."""
    create_res = client.post(
        "/api/attendance/",
        json={"student_id": sample_student["student_id"], "date": "2026-10-01", "status": "absent"},
        headers=admin_headers,
    )
    att_id = create_res.json()["attendance_id"]

    res = client.delete(f"/api/attendance/{att_id}", headers=student_headers)
    assert res.status_code == 403


# ==============================================================================
# 3. Validation & Conflict Handling
# ==============================================================================

def test_invalid_status_rejected(client, admin_headers, sample_student):
    """Invalid status string rejected with HTTP 422."""
    payload = {
        "student_id": sample_student["student_id"],
        "date": "2026-10-01",
        "status": "super_present",  # Invalid
    }
    res = client.post("/api/attendance/", json=payload, headers=admin_headers)
    assert res.status_code == 422


def test_nonexistent_student_rejected(client, admin_headers):
    """Attendance for a nonexistent student returns HTTP 404."""
    payload = {
        "student_id": "STU-NONEXISTENT-999",
        "date": "2026-10-01",
        "status": "present",
    }
    res = client.post("/api/attendance/", json=payload, headers=admin_headers)
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_duplicate_student_date_rejected(client, admin_headers, sample_student):
    """Duplicate attendance for same student and date returns HTTP 409 Conflict."""
    payload = {
        "student_id": sample_student["student_id"],
        "date": "2026-10-01",
        "status": "present",
    }
    res1 = client.post("/api/attendance/", json=payload, headers=admin_headers)
    assert res1.status_code == 201

    # Second attempt with same student and date
    res2 = client.post("/api/attendance/", json=payload, headers=admin_headers)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"].lower()


# ==============================================================================
# 4. Student Self-Attendance (/api/attendance/me & /api/attendance/me/summary)
# ==============================================================================

def test_student_can_access_own_attendance_me(client, admin_headers, student_headers, sample_student, sample_student_beta):
    """Student receives only their own attendance via /api/attendance/me."""
    # Seed attendance for student Alpha
    client.post(
        "/api/attendance/",
        json={"student_id": sample_student["student_id"], "date": "2026-10-01", "status": "present"},
        headers=admin_headers,
    )
    client.post(
        "/api/attendance/",
        json={"student_id": sample_student["student_id"], "date": "2026-10-02", "status": "absent"},
        headers=admin_headers,
    )

    # Seed attendance for student Beta
    client.post(
        "/api/attendance/",
        json={"student_id": sample_student_beta["student_id"], "date": "2026-10-01", "status": "late"},
        headers=admin_headers,
    )

    # Student Alpha calls /me
    res = client.get("/api/attendance/me", headers=student_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 2
    assert all(item["student_id"] == "STU-2024-001" for item in data["items"])


def test_student_can_access_own_attendance_me_summary(client, admin_headers, student_headers, sample_student):
    """Student receives calculated metrics via /api/attendance/me/summary."""
    # Seed records: 2 present, 1 absent, 1 late
    client.post("/api/attendance/", json={"student_id": sample_student["student_id"], "date": "2026-10-01", "status": "present"}, headers=admin_headers)
    client.post("/api/attendance/", json={"student_id": sample_student["student_id"], "date": "2026-10-02", "status": "present"}, headers=admin_headers)
    client.post("/api/attendance/", json={"student_id": sample_student["student_id"], "date": "2026-10-03", "status": "absent"}, headers=admin_headers)
    client.post("/api/attendance/", json={"student_id": sample_student["student_id"], "date": "2026-10-04", "status": "late"}, headers=admin_headers)

    res = client.get("/api/attendance/me/summary", headers=student_headers)
    assert res.status_code == 200
    summary = res.json()
    assert summary["student_id"] == "STU-2024-001"
    assert summary["total_days"] == 4
    assert summary["present_days"] == 2
    assert summary["absent_days"] == 1
    assert summary["late_days"] == 1
    assert summary["excused_days"] == 0
    assert summary["attendance_percentage"] == 50.0  # 2/4 = 50%


def test_student_cannot_access_another_student_attendance(client, student_headers, sample_student_beta):
    """Student is blocked from accessing administrative student attendance routes."""
    res_list = client.get(f"/api/attendance/student/{sample_student_beta['student_id']}", headers=student_headers)
    assert res_list.status_code == 403

    res_summary = client.get(f"/api/attendance/student/{sample_student_beta['student_id']}/summary", headers=student_headers)
    assert res_summary.status_code == 403


def test_non_student_cannot_access_attendance_me(client, teacher_headers):
    """Teacher calling /api/attendance/me is forbidden (HTTP 403)."""
    res = client.get("/api/attendance/me", headers=teacher_headers)
    assert res.status_code == 403


# ==============================================================================
# 5. Filtering & Pagination Tests
# ==============================================================================

def test_attendance_filtering_and_pagination(client, admin_headers, sample_student, sample_student_beta):
    """Test date, date range, status, student_id filtering and pagination."""
    # Seed attendance over multiple dates
    dates = ["2026-10-01", "2026-10-02", "2026-10-03", "2026-10-04", "2026-10-05"]
    statuses = ["present", "absent", "late", "excused", "present"]

    for d, s in zip(dates, statuses):
        client.post(
            "/api/attendance/",
            json={"student_id": sample_student["student_id"], "date": d, "status": s},
            headers=admin_headers,
        )

    # Filter by specific date
    date_res = client.get("/api/attendance/?date=2026-10-03", headers=admin_headers)
    assert date_res.status_code == 200
    assert date_res.json()["total"] == 1
    assert date_res.json()["items"][0]["status"] == "late"

    # Filter by date range
    range_res = client.get("/api/attendance/?start_date=2026-10-02&end_date=2026-10-04", headers=admin_headers)
    assert range_res.status_code == 200
    assert range_res.json()["total"] == 3

    # Filter by status
    status_res = client.get("/api/attendance/?status=present", headers=admin_headers)
    assert status_res.status_code == 200
    assert status_res.json()["total"] == 2

    # Test Pagination (page=1, limit=2)
    p_res = client.get("/api/attendance/?page=1&limit=2", headers=admin_headers)
    assert p_res.status_code == 200
    p_data = p_res.json()
    assert len(p_data["items"]) == 2
    assert p_data["page"] == 1
    assert p_data["limit"] == 2
    assert p_data["total"] == 5
    assert p_data["pages"] == 3


# ==============================================================================
# 6. Summary Calculation & Zero Records Safety
# ==============================================================================

def test_attendance_summary_for_student_endpoint(client, teacher_headers, sample_student):
    """Teacher fetches attendance summary via /api/attendance/student/{student_id}/summary."""
    client.post("/api/attendance/", json={"student_id": sample_student["student_id"], "date": "2026-10-01", "status": "present"}, headers=teacher_headers)
    client.post("/api/attendance/", json={"student_id": sample_student["student_id"], "date": "2026-10-02", "status": "present"}, headers=teacher_headers)
    client.post("/api/attendance/", json={"student_id": sample_student["student_id"], "date": "2026-10-03", "status": "present"}, headers=teacher_headers)

    res = client.get(f"/api/attendance/student/{sample_student['student_id']}/summary", headers=teacher_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_days"] == 3
    assert data["present_days"] == 3
    assert data["absent_days"] == 0
    assert data["attendance_percentage"] == 100.0


def test_attendance_summary_zero_records_safe(client, teacher_headers, sample_student):
    """Zero attendance records safely yields 0.0 percentage without DivisionByZero."""
    res = client.get(f"/api/attendance/student/{sample_student['student_id']}/summary", headers=teacher_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_days"] == 0
    assert data["present_days"] == 0
    assert data["absent_days"] == 0
    assert data["late_days"] == 0
    assert data["excused_days"] == 0
    assert data["attendance_percentage"] == 0.0
