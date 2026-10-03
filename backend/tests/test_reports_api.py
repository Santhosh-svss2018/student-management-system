"""
Tests for Reports & Data Export Module
Verifies filtered institutional reports, CSV streaming exports, PDF generation, and RBAC authorization.
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
def other_student_user(mock_db):
    user_doc = {
        "_id": ObjectId(),
        "full_name": "Priya Sharma",
        "email": "priya.sharma@student.edumanage.com",
        "department": "Information Technology",
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
def seeded_report_data(mock_db):
    """Seed sample students, attendance, and marks."""
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
    mock_db.students.insert_many([s1, s2])

    mock_db.attendance.insert_many([
        {"attendance_id": "ATT-001", "student_id": "STU-001", "date": "2026-10-01", "status": "present", "remarks": "On time", "marked_by": "Prof. Marcus"},
        {"attendance_id": "ATT-002", "student_id": "STU-002", "date": "2026-10-01", "status": "absent", "remarks": "Sick leave", "marked_by": "Prof. Marcus"},
    ])

    mock_db.marks.insert_many([
        {
            "marks_id": "MRK-001",
            "student_id": "STU-001",
            "subject_code": "CS-301",
            "subject_name": "Algorithms",
            "semester": 5,
            "exam_type": "semester",
            "marks_obtained": 88.0,
            "max_marks": 100.0,
            "percentage": 88.0,
            "grade": "A+",
            "academic_year": "2024-2025",
            "entered_by": "Prof. Marcus",
        },
        {
            "marks_id": "MRK-002",
            "student_id": "STU-002",
            "subject_code": "IT-201",
            "subject_name": "Web Tech",
            "semester": 3,
            "exam_type": "internal_1",
            "marks_obtained": 45.0,
            "max_marks": 50.0,
            "percentage": 90.0,
            "grade": "A+",
            "academic_year": "2024-2025",
            "entered_by": "Prof. Marcus",
        },
    ])

    return {"s1": s1, "s2": s2}


# =====================================================================
# 1. AUTHENTICATION & RBAC TESTS
# =====================================================================

def test_unauthenticated_reports_returns_401(client):
    """Unauthenticated requests to reports endpoints must return 401."""
    assert client.get("/api/reports/students").status_code == 401
    assert client.get("/api/reports/attendance").status_code == 401
    assert client.get("/api/reports/marks").status_code == 401
    assert client.get("/api/reports/academic-summary").status_code == 401
    assert client.get("/api/reports/students/export").status_code == 401
    assert client.get("/api/reports/student/STU-001/pdf").status_code == 401


def test_student_cannot_access_institutional_reports(client, student_headers):
    """Students cannot access institutional reports (403 Forbidden)."""
    assert client.get("/api/reports/students", headers=student_headers).status_code == 403
    assert client.get("/api/reports/attendance", headers=student_headers).status_code == 403
    assert client.get("/api/reports/marks", headers=student_headers).status_code == 403
    assert client.get("/api/reports/academic-summary", headers=student_headers).status_code == 403
    assert client.get("/api/reports/students/export", headers=student_headers).status_code == 403


def test_admin_and_teacher_can_access_reports(client, admin_headers, teacher_headers, seeded_report_data):
    """Admin and Teacher can query reports."""
    res1 = client.get("/api/reports/students", headers=admin_headers)
    assert res1.status_code == 200
    assert res1.json()["total"] == 2

    res2 = client.get("/api/reports/attendance", headers=teacher_headers)
    assert res2.status_code == 200
    assert res2.json()["total"] == 2

    res3 = client.get("/api/reports/marks", headers=admin_headers)
    assert res3.status_code == 200
    assert res3.json()["total"] == 2


# =====================================================================
# 2. FILTERING TESTS
# =====================================================================

def test_students_report_filters(client, admin_headers, seeded_report_data):
    """Students report can filter by department, year, and search query."""
    res_dept = client.get("/api/reports/students?department=Computer%20Science", headers=admin_headers)
    assert res_dept.status_code == 200
    assert res_dept.json()["total"] == 1
    assert res_dept.json()["items"][0]["student_id"] == "STU-001"

    res_search = client.get("/api/reports/students?search=Priya", headers=admin_headers)
    assert res_search.status_code == 200
    assert res_search.json()["total"] == 1
    assert res_search.json()["items"][0]["student_id"] == "STU-002"


def test_attendance_report_filters(client, admin_headers, seeded_report_data):
    """Attendance report can filter by status and date."""
    res_status = client.get("/api/reports/attendance?status=absent", headers=admin_headers)
    assert res_status.status_code == 200
    assert res_status.json()["total"] == 1
    assert res_status.json()["items"][0]["student_id"] == "STU-002"


def test_marks_report_filters(client, admin_headers, seeded_report_data):
    """Marks report can filter by subject code and semester."""
    res_subject = client.get("/api/reports/marks?subject_code=CS-301", headers=admin_headers)
    assert res_subject.status_code == 200
    assert res_subject.json()["total"] == 1
    assert res_subject.json()["items"][0]["subject_code"] == "CS-301"


def test_academic_summary_report(client, admin_headers, seeded_report_data):
    """Academic summary report computes aggregate pass percentages."""
    res = client.get("/api/reports/academic-summary", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert "summary" in data
    assert data["summary"]["pass_percentage"] == 100.0
    assert len(data["students"]) == 2


# =====================================================================
# 3. CSV EXPORT TESTS
# =====================================================================

def test_export_students_csv(client, admin_headers, seeded_report_data):
    """Exporting students CSV returns valid text/csv and correct headers."""
    res = client.get("/api/reports/students/export", headers=admin_headers)
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "attachment" in res.headers["content-disposition"]
    content = res.text
    assert "Student ID,Roll Number,Full Name" in content
    assert "STU-001" in content
    assert "Arun Kumar" in content


def test_export_attendance_csv(client, teacher_headers, seeded_report_data):
    """Exporting attendance CSV returns valid text/csv."""
    res = client.get("/api/reports/attendance/export", headers=teacher_headers)
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    content = res.text
    assert "Attendance ID,Student ID,Student Name" in content
    assert "ATT-001" in content


def test_export_marks_csv(client, admin_headers, seeded_report_data):
    """Exporting marks CSV returns valid text/csv."""
    res = client.get("/api/reports/marks/export", headers=admin_headers)
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    content = res.text
    assert "Marks ID,Student ID,Student Name" in content
    assert "MRK-001" in content
    assert "Algorithms" in content


# =====================================================================
# 4. PDF EXPORT & ISOLATION TESTS
# =====================================================================

def test_admin_can_download_student_pdf(client, admin_headers, seeded_report_data):
    """Admin can download PDF academic report for any student."""
    res = client.get("/api/reports/student/STU-001/pdf", headers=admin_headers)
    assert res.status_code == 200
    assert "application/pdf" in res.headers["content-type"]
    assert res.content.startswith(b"%PDF-")


def test_student_can_download_own_pdf(client, student_headers, seeded_report_data):
    """Student can download their own PDF report."""
    res = client.get("/api/reports/student/STU-001/pdf", headers=student_headers)
    assert res.status_code == 200
    assert "application/pdf" in res.headers["content-type"]
    assert res.content.startswith(b"%PDF-")


def test_student_cannot_download_other_student_pdf(client, student_headers, seeded_report_data):
    """Student cannot download another student's PDF report (403 Forbidden)."""
    res = client.get("/api/reports/student/STU-002/pdf", headers=student_headers)
    assert res.status_code == 403


def test_pdf_download_nonexistent_student_returns_404(client, admin_headers):
    """Downloading PDF for non-existent student returns 404 Not Found."""
    res = client.get("/api/reports/student/NONEXISTENT-999/pdf", headers=admin_headers)
    assert res.status_code == 404
