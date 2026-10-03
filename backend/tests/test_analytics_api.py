"""
Tests for Analytics & Institutional Metrics Module
Verifies Admin overview, Department analytics, Academic analytics, Attendance analytics,
Teacher overview, Student self analytics, and RBAC security rules.
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
        "full_name": "Prof. Marcus Vance",
        "email": "marcus.vance@edumanage.com",
        "department": "Computer Science",
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
        "full_name": "Arun Kumar",
        "email": "arun.kumar@student.edumanage.com",
        "department": "Computer Science",
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
def seeded_environment(mock_db):
    """Seed comprehensive students, attendance, and marks records."""
    s1 = {
        "_id": ObjectId(),
        "student_id": "STU-001",
        "full_name": "Arun Kumar",
        "email": "arun.kumar@student.edumanage.com",
        "department": "Computer Science",
        "year": 3,
        "section": "A",
        "roll_number": "CS-001",
        "is_active": True,
    }
    s2 = {
        "_id": ObjectId(),
        "student_id": "STU-002",
        "full_name": "Priya Sharma",
        "email": "priya.sharma@student.edumanage.com",
        "department": "Information Technology",
        "year": 2,
        "section": "B",
        "roll_number": "IT-002",
        "is_active": True,
    }
    s3 = {
        "_id": ObjectId(),
        "student_id": "STU-003",
        "full_name": "Rahul Verma",
        "email": "rahul.verma@student.edumanage.com",
        "department": "Computer Science",
        "year": 3,
        "section": "A",
        "roll_number": "CS-003",
        "is_active": False,
    }
    mock_db.students.insert_many([s1, s2, s3])

    # Attendance for s1 (100% attendance)
    mock_db.attendance.insert_many([
        {"attendance_id": "ATT-1", "student_id": "STU-001", "date": "2026-10-01", "status": "present", "marked_by": "Prof. Marcus"},
        {"attendance_id": "ATT-2", "student_id": "STU-001", "date": "2026-10-02", "status": "present", "marked_by": "Prof. Marcus"},
    ])
    # Attendance for s2 (50% attendance - defaulter)
    mock_db.attendance.insert_many([
        {"attendance_id": "ATT-3", "student_id": "STU-002", "date": "2026-10-01", "status": "present", "marked_by": "Prof. Marcus"},
        {"attendance_id": "ATT-4", "student_id": "STU-002", "date": "2026-10-02", "status": "absent", "marked_by": "Prof. Marcus"},
    ])

    # Marks for s1 (High grades)
    mock_db.marks.insert_many([
        {
            "marks_id": "MRK-1",
            "student_id": "STU-001",
            "subject_code": "CS-301",
            "subject_name": "Algorithms",
            "semester": 5,
            "exam_type": "semester",
            "marks_obtained": 90.0,
            "max_marks": 100.0,
            "percentage": 90.0,
            "grade": "A+",
            "academic_year": "2024-2025",
            "entered_by": "Prof. Marcus",
        },
        {
            "marks_id": "MRK-2",
            "student_id": "STU-001",
            "subject_code": "CS-302",
            "subject_name": "Databases",
            "semester": 5,
            "exam_type": "semester",
            "marks_obtained": 80.0,
            "max_marks": 100.0,
            "percentage": 80.0,
            "grade": "A",
            "academic_year": "2024-2025",
            "entered_by": "Prof. Marcus",
        },
    ])
    # Marks for s2 (Low grades)
    mock_db.marks.insert_one({
        "marks_id": "MRK-3",
        "student_id": "STU-002",
        "subject_code": "IT-201",
        "subject_name": "Web Tech",
        "semester": 3,
        "exam_type": "semester",
        "marks_obtained": 35.0,
        "max_marks": 100.0,
        "percentage": 35.0,
        "grade": "F",
        "academic_year": "2024-2025",
        "entered_by": "Prof. Marcus",
    })

    return {"s1": s1, "s2": s2, "s3": s3}


# =====================================================================
# 1. AUTHENTICATION & RBAC TESTS
# =====================================================================

def test_unauthenticated_analytics_returns_401(client):
    """Unauthenticated requests to any analytics endpoint must return 401."""
    assert client.get("/api/analytics/admin/overview").status_code == 401
    assert client.get("/api/analytics/admin/departments").status_code == 401
    assert client.get("/api/analytics/admin/academic").status_code == 401
    assert client.get("/api/analytics/admin/attendance").status_code == 401
    assert client.get("/api/analytics/teacher/overview").status_code == 401
    assert client.get("/api/analytics/student/me").status_code == 401


def test_non_admin_cannot_access_admin_analytics(client, teacher_headers, student_headers):
    """Teacher and Student cannot access Admin Analytics endpoints (403 Forbidden)."""
    endpoints = [
        "/api/analytics/admin/overview",
        "/api/analytics/admin/departments",
        "/api/analytics/admin/academic",
        "/api/analytics/admin/attendance",
    ]
    for ep in endpoints:
        assert client.get(ep, headers=teacher_headers).status_code == 403
        assert client.get(ep, headers=student_headers).status_code == 403


def test_student_cannot_access_teacher_overview(client, student_headers):
    """Student role cannot access Teacher overview endpoint."""
    res = client.get("/api/analytics/teacher/overview", headers=student_headers)
    assert res.status_code == 403


def test_non_student_cannot_access_student_me(client, admin_headers, teacher_headers):
    """Admin and Teacher roles cannot access student self analytics."""
    assert client.get("/api/analytics/student/me", headers=admin_headers).status_code == 403
    assert client.get("/api/analytics/student/me", headers=teacher_headers).status_code == 403


# =====================================================================
# 2. ADMIN ANALYTICS TESTS
# =====================================================================

def test_admin_overview_empty_db(client, admin_headers):
    """Admin overview with empty database returns 0 counts and safe percentages."""
    res = client.get("/api/analytics/admin/overview", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_students"] == 0
    assert data["active_students"] == 0
    assert data["overall_attendance_percentage"] == 0.0
    assert data["overall_academic_percentage"] == 0.0
    assert data["students_at_risk"] == 0


def test_admin_overview_with_data(client, admin_headers, seeded_environment):
    """Admin overview calculates correct live metrics."""
    res = client.get("/api/analytics/admin/overview", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_students"] == 3
    assert data["active_students"] == 2
    assert data["inactive_students"] == 1
    assert data["total_attendance_records"] == 4
    # 3 present out of 4 = 75.0%
    assert data["overall_attendance_percentage"] == 75.0
    assert data["total_marks_records"] == 3
    # 90 + 80 + 35 = 205 / 300 = 68.33%
    assert data["overall_academic_percentage"] == 68.33
    assert len(data["department_distribution"]) > 0


def test_admin_departments_analytics(client, admin_headers, seeded_environment):
    """Admin departments endpoint groups metrics per department correctly."""
    res = client.get("/api/analytics/admin/departments", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_departments"] == 2
    dept_names = [d["department"] for d in data["departments"]]
    assert "Computer Science" in dept_names
    assert "Information Technology" in dept_names

    cs_dept = next(d for d in data["departments"] if d["department"] == "Computer Science")
    assert cs_dept["student_count"] == 1
    assert cs_dept["attendance_percentage"] == 100.0


def test_admin_academic_analytics(client, admin_headers, seeded_environment):
    """Admin academic endpoint aggregates grades and subject performance."""
    res = client.get("/api/analytics/admin/academic", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_marks_evaluated"] == 3
    assert data["grade_distribution"]["A+"] == 1
    assert data["grade_distribution"]["A"] == 1
    assert data["grade_distribution"]["F"] == 1
    assert data["pass_percentage"] == 66.67
    assert data["fail_percentage"] == 33.33
    assert len(data["subject_performance"]) == 3


def test_admin_attendance_analytics(client, admin_headers, seeded_environment):
    """Admin attendance endpoint calculates trends and flags defaulters."""
    res = client.get("/api/analytics/admin/attendance", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["overall_attendance"] == 75.0
    assert data["present_percentage"] == 75.0
    assert data["absent_percentage"] == 25.0
    assert len(data["attendance_trend"]) == 2
    # Defaulter check: STU-002 has 50% attendance (< 75%)
    defaulters = data["attendance_defaulters"]
    assert len(defaulters) == 1
    assert defaulters[0]["student_id"] == "STU-002"
    assert defaulters[0]["attendance_percentage"] == 50.0


# =====================================================================
# 3. TEACHER & STUDENT ANALYTICS TESTS
# =====================================================================

def test_teacher_overview_analytics(client, teacher_headers, seeded_environment):
    """Teacher overview endpoint provides authorized class metrics."""
    res = client.get("/api/analytics/teacher/overview", headers=teacher_headers)
    assert res.status_code == 200
    data = res.json()
    assert "student_count" in data
    assert "attendance_overview" in data
    assert "academic_performance" in data
    assert "grade_distribution" in data


def test_student_self_analytics(client, student_headers, seeded_environment):
    """Student can retrieve only their personal attendance, marks, and risk analysis."""
    res = client.get("/api/analytics/student/me", headers=student_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["student_id"] == "STU-001"
    assert data["student_name"] == "Arun Kumar"
    assert data["attendance_percentage"] == 100.0
    assert data["academic_percentage"] == 85.0
    assert data["passed_subjects"] == 2
    assert data["failed_subjects"] == 0
    assert data["risk_level"] == "LOW"
