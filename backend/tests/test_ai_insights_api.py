"""
Tests for AI Insights & Student Risk Analysis Module
Verifies risk score calculations, explainable factor and recommendation generation,
RBAC authorization rules (Admin, Teacher, Student), student self-service, and institutional risk overviews.
"""

from bson import ObjectId
import pytest
from app.core.security import create_access_token, get_password_hash
from app.models.ai_insights import RiskLevel, determine_risk_level


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


# =====================================================================
# 1. AUTHENTICATION & RBAC TESTS
# =====================================================================

def test_unauthenticated_request_returns_401(client, sample_student):
    """Unauthenticated requests to AI Insights must return 401 Unauthorized."""
    res1 = client.get("/api/ai-insights/students")
    assert res1.status_code == 401

    res2 = client.get(f"/api/ai-insights/student/{sample_student['student_id']}")
    assert res2.status_code == 401

    res3 = client.get("/api/ai-insights/me")
    assert res3.status_code == 401


def test_invalid_jwt_returns_401(client):
    """Requests with malformed JWT tokens must return 401 Unauthorized."""
    headers = {"Authorization": "Bearer invalid.fake.token"}
    res = client.get("/api/ai-insights/students", headers=headers)
    assert res.status_code == 401


def test_admin_and_teacher_can_access_student_risk(client, admin_headers, teacher_headers, sample_student):
    """Admin and Teacher can inspect specific student risk analyses."""
    res_admin = client.get(f"/api/ai-insights/student/{sample_student['student_id']}", headers=admin_headers)
    assert res_admin.status_code == 200
    assert res_admin.json()["student_id"] == sample_student["student_id"]

    res_teacher = client.get(f"/api/ai-insights/student/{sample_student['student_id']}", headers=teacher_headers)
    assert res_teacher.status_code == 200
    assert res_teacher.json()["student_id"] == sample_student["student_id"]


def test_student_cannot_access_other_student_risk(client, student_headers, sample_student_beta):
    """Students cannot inspect other students' risk analyses (403 Forbidden)."""
    res = client.get(
        f"/api/ai-insights/student/{sample_student_beta['student_id']}",
        headers=student_headers,
    )
    assert res.status_code == 403


def test_admin_and_teacher_can_access_institutional_overview(client, admin_headers, teacher_headers):
    """Admin and Teacher can view the institutional risk overview."""
    res_admin = client.get("/api/ai-insights/students", headers=admin_headers)
    assert res_admin.status_code == 200
    assert "total_students_analyzed" in res_admin.json()

    res_teacher = client.get("/api/ai-insights/students", headers=teacher_headers)
    assert res_teacher.status_code == 200
    assert "total_students_analyzed" in res_teacher.json()


def test_student_cannot_access_institutional_overview(client, student_headers):
    """Students cannot access the institutional risk overview."""
    res = client.get("/api/ai-insights/students", headers=student_headers)
    assert res.status_code == 403


def test_student_can_access_own_risk_me(client, student_headers, sample_student):
    """Student can retrieve only their own risk analysis via /api/ai-insights/me."""
    res = client.get("/api/ai-insights/me", headers=student_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["student_id"] == sample_student["student_id"]
    assert data["student_name"] == sample_student["full_name"]


def test_non_student_cannot_access_risk_me(client, admin_headers, teacher_headers):
    """Admin and Teacher cannot use /api/ai-insights/me (student role only)."""
    res_admin = client.get("/api/ai-insights/me", headers=admin_headers)
    assert res_admin.status_code == 403

    res_teacher = client.get("/api/ai-insights/me", headers=teacher_headers)
    assert res_teacher.status_code == 403


def test_nonexistent_student_returns_404(client, admin_headers):
    """Requesting risk analysis for an unknown student ID returns 404 Not Found."""
    res = client.get("/api/ai-insights/student/NONEXISTENT-ID-999", headers=admin_headers)
    assert res.status_code == 404


# =====================================================================
# 2. RISK SCORING, FACTOR & RECOMMENDATION TESTS
# =====================================================================

def test_low_risk_student_high_attendance_high_marks(client, teacher_headers, sample_student):
    """
    Student with 100% attendance (2 sessions) and 90% marks (2 assessments):
    performance = (100 * 0.4) + (90 * 0.6) = 40 + 54 = 94.0
    base_risk = 100 - 94 = 6.0
    failed_penalty = 0
    risk_score = 6.0 -> LOW
    """
    # 2 Present sessions
    client.post("/api/attendance/", json={
        "student_id": sample_student["student_id"],
        "date": "2026-10-01",
        "status": "present",
    }, headers=teacher_headers)
    client.post("/api/attendance/", json={
        "student_id": sample_student["student_id"],
        "date": "2026-10-02",
        "status": "present",
    }, headers=teacher_headers)

    # 2 High score marks
    client.post("/api/marks/", json={
        "student_id": sample_student["student_id"],
        "subject_code": "CS-301",
        "subject_name": "Algorithms",
        "semester": 5,
        "exam_type": "semester",
        "marks_obtained": 90.0,
        "max_marks": 100.0,
        "academic_year": "2024-2025",
    }, headers=teacher_headers)
    client.post("/api/marks/", json={
        "student_id": sample_student["student_id"],
        "subject_code": "CS-302",
        "subject_name": "Databases",
        "semester": 5,
        "exam_type": "semester",
        "marks_obtained": 90.0,
        "max_marks": 100.0,
        "academic_year": "2024-2025",
    }, headers=teacher_headers)

    res = client.get(f"/api/ai-insights/student/{sample_student['student_id']}", headers=teacher_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["risk_score"] == 6.0
    assert data["risk_level"] == "LOW"
    assert data["attendance_percentage"] == 100.0
    assert data["academic_percentage"] == 90.0
    assert data["failed_assessments"] == 0

    # Verify explainable key factors & recommendations
    factors = " ".join(data["key_factors"])
    assert "Attendance is excellent" in factors or "90" in factors
    assert "Strong academic performance" in factors

    recs = " ".join(data["recommendations"])
    assert "Maintain current attendance" in recs


def test_high_risk_student_low_attendance_failed_assessments(client, teacher_headers, sample_student_beta):
    """
    Student with 50% attendance (1 present, 1 absent) and failed assessments:
    attendance = 50%
    marks = 30% (score 30/100, failed)
    performance = (50 * 0.4) + (30 * 0.6) = 20 + 18 = 38.0
    base_risk = 100 - 38 = 62.0
    failed penalty = 1 * 5 = 5.0
    risk_score = 67.0 -> HIGH
    """
    client.post("/api/attendance/", json={
        "student_id": sample_student_beta["student_id"],
        "date": "2026-10-01",
        "status": "present",
    }, headers=teacher_headers)
    client.post("/api/attendance/", json={
        "student_id": sample_student_beta["student_id"],
        "date": "2026-10-02",
        "status": "absent",
    }, headers=teacher_headers)

    client.post("/api/marks/", json={
        "student_id": sample_student_beta["student_id"],
        "subject_code": "IT-201",
        "subject_name": "Data Structures",
        "semester": 3,
        "exam_type": "semester",
        "marks_obtained": 30.0,
        "max_marks": 100.0,
        "academic_year": "2024-2025",
    }, headers=teacher_headers)

    res = client.get(f"/api/ai-insights/student/{sample_student_beta['student_id']}", headers=teacher_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["risk_score"] == 67.0
    assert data["risk_level"] == "HIGH"
    assert data["failed_assessments"] == 1

    factors = " ".join(data["key_factors"])
    assert "below the mandatory 75%" in factors
    assert "failed 1 assessment" in factors

    recs = " ".join(data["recommendations"])
    assert "Improve class attendance" in recs
    assert "Review failed course modules" in recs
    assert "academic counselor" in recs


def test_empty_academic_records_defaults_safely(client, admin_headers, sample_student):
    """Student with zero attendance and zero marks records defaults safely to 0.0 risk score."""
    res = client.get(f"/api/ai-insights/student/{sample_student['student_id']}", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["risk_score"] == 0.0
    assert data["risk_level"] == "LOW"
    assert data["failed_assessments"] == 0
    assert data["total_attendance_days"] == 0
    assert data["total_assessments"] == 0


def test_risk_level_threshold_function():
    """Verifies standard categorical risk bands."""
    assert determine_risk_level(0.0) == RiskLevel.LOW
    assert determine_risk_level(24.99) == RiskLevel.LOW
    assert determine_risk_level(25.0) == RiskLevel.MEDIUM
    assert determine_risk_level(49.99) == RiskLevel.MEDIUM
    assert determine_risk_level(50.0) == RiskLevel.HIGH
    assert determine_risk_level(74.99) == RiskLevel.HIGH
    assert determine_risk_level(75.0) == RiskLevel.CRITICAL
    assert determine_risk_level(100.0) == RiskLevel.CRITICAL
