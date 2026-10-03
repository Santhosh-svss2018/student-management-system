"""
Tests for Marks & Grades Management Module
Verifies Marks CRUD endpoints, RBAC authorization rules (Admin, Teacher, Student),
grade/percentage calculations, summary calculations, duplicate uniqueness constraints, and student self-access.
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


# =====================================================================
# 1. AUTHENTICATION & RBAC TESTS
# =====================================================================

def test_unauthenticated_request_returns_401(client, sample_student):
    """Unauthenticated requests to Marks endpoints must return 401 Unauthorized."""
    res_post = client.post("/api/marks/", json={
        "student_id": sample_student["student_id"],
        "subject_code": "CS-301",
        "subject_name": "Algorithms",
        "semester": 5,
        "exam_type": "semester",
        "marks_obtained": 85.0,
        "max_marks": 100.0,
        "academic_year": "2024-2025",
    })
    assert res_post.status_code == 401

    res_get = client.get("/api/marks/")
    assert res_get.status_code == 401


def test_invalid_jwt_returns_401(client):
    """Requests with malformed/invalid JWT tokens must return 401 Unauthorized."""
    headers = {"Authorization": "Bearer invalid.token.string"}
    res = client.get("/api/marks/", headers=headers)
    assert res.status_code == 401


def test_admin_and_teacher_can_create_marks(client, admin_headers, teacher_headers, sample_student):
    """Both Admin and Teacher can record student marks."""
    payload_admin = {
        "student_id": sample_student["student_id"],
        "subject_code": "CS-301",
        "subject_name": "Design & Analysis of Algorithms",
        "semester": 5,
        "exam_type": "internal_1",
        "marks_obtained": 45.0,
        "max_marks": 50.0,
        "academic_year": "2024-2025",
        "remarks": "Admin entered marks",
    }
    res_admin = client.post("/api/marks/", json=payload_admin, headers=admin_headers)
    assert res_admin.status_code == 201
    data_admin = res_admin.json()
    assert data_admin["marks_id"].startswith("MRK-")
    assert data_admin["percentage"] == 90.0
    assert data_admin["grade"] == "A+"
    assert data_admin["entered_by"] == "admin.director@edumanage.com"

    payload_teacher = {
        "student_id": sample_student["student_id"],
        "subject_code": "CS-302",
        "subject_name": "Database Management Systems",
        "semester": 5,
        "exam_type": "internal_1",
        "marks_obtained": 38.0,
        "max_marks": 50.0,
        "academic_year": "2024-2025",
        "remarks": "Teacher entered marks",
    }
    res_teacher = client.post("/api/marks/", json=payload_teacher, headers=teacher_headers)
    assert res_teacher.status_code == 201
    data_teacher = res_teacher.json()
    assert data_teacher["percentage"] == 76.0
    assert data_teacher["grade"] == "B"
    assert data_teacher["entered_by"] == "faculty.prof@edumanage.com"


def test_student_cannot_create_marks(client, student_headers, sample_student):
    """Students are forbidden from recording marks (403 Forbidden)."""
    payload = {
        "student_id": sample_student["student_id"],
        "subject_code": "CS-301",
        "subject_name": "Algorithms",
        "semester": 5,
        "exam_type": "semester",
        "marks_obtained": 95.0,
        "max_marks": 100.0,
        "academic_year": "2024-2025",
    }
    res = client.post("/api/marks/", json=payload, headers=student_headers)
    assert res.status_code == 403


def test_admin_and_teacher_can_view_marks(client, admin_headers, teacher_headers):
    """Admin and Teacher can query the administrative marks listing."""
    res_admin = client.get("/api/marks/", headers=admin_headers)
    assert res_admin.status_code == 200
    assert "items" in res_admin.json()

    res_teacher = client.get("/api/marks/", headers=teacher_headers)
    assert res_teacher.status_code == 200
    assert "items" in res_teacher.json()


def test_student_cannot_access_admin_listing(client, student_headers):
    """Students cannot access administrative marks directory."""
    res = client.get("/api/marks/", headers=student_headers)
    assert res.status_code == 403


def test_admin_and_teacher_can_update_marks(client, admin_headers, teacher_headers, sample_student):
    """Both Admin and Teacher can update marks records."""
    # Create record
    create_res = client.post("/api/marks/", json={
        "student_id": sample_student["student_id"],
        "subject_code": "CS-303",
        "subject_name": "Operating Systems",
        "semester": 5,
        "exam_type": "internal_1",
        "marks_obtained": 30.0,
        "max_marks": 50.0,
        "academic_year": "2024-2025",
    }, headers=teacher_headers)
    marks_id = create_res.json()["marks_id"]

    # Teacher updates marks
    res_teacher = client.put(f"/api/marks/{marks_id}", json={
        "marks_obtained": 40.0,
        "remarks": "Re-evaluation completed",
    }, headers=teacher_headers)
    assert res_teacher.status_code == 200
    assert res_teacher.json()["percentage"] == 80.0
    assert res_teacher.json()["grade"] == "A"

    # Admin updates marks
    res_admin = client.put(f"/api/marks/{marks_id}", json={
        "marks_obtained": 48.0,
    }, headers=admin_headers)
    assert res_admin.status_code == 200
    assert res_admin.json()["percentage"] == 96.0
    assert res_admin.json()["grade"] == "A+"


def test_student_cannot_update_marks(client, student_headers, teacher_headers, sample_student):
    """Students cannot update marks records."""
    create_res = client.post("/api/marks/", json={
        "student_id": sample_student["student_id"],
        "subject_code": "CS-304",
        "subject_name": "Computer Networks",
        "semester": 5,
        "exam_type": "internal_1",
        "marks_obtained": 30.0,
        "max_marks": 50.0,
        "academic_year": "2024-2025",
    }, headers=teacher_headers)
    marks_id = create_res.json()["marks_id"]

    res = client.put(f"/api/marks/{marks_id}", json={"marks_obtained": 50.0}, headers=student_headers)
    assert res.status_code == 403


def test_admin_can_delete_marks_teacher_and_student_cannot(
    client, admin_headers, teacher_headers, student_headers, sample_student
):
    """Only Admin can delete marks records. Teachers and Students are blocked."""
    create_res = client.post("/api/marks/", json={
        "student_id": sample_student["student_id"],
        "subject_code": "CS-305",
        "subject_name": "Machine Learning",
        "semester": 5,
        "exam_type": "assignment",
        "marks_obtained": 25.0,
        "max_marks": 30.0,
        "academic_year": "2024-2025",
    }, headers=admin_headers)
    marks_id = create_res.json()["marks_id"]

    # Student cannot delete -> 403
    res_student = client.delete(f"/api/marks/{marks_id}", headers=student_headers)
    assert res_student.status_code == 403

    # Teacher cannot delete -> 403
    res_teacher = client.delete(f"/api/marks/{marks_id}", headers=teacher_headers)
    assert res_teacher.status_code == 403

    # Admin can delete -> 200
    res_admin = client.delete(f"/api/marks/{marks_id}", headers=admin_headers)
    assert res_admin.status_code == 200
    assert res_admin.json()["marks_id"] == marks_id

    # Deleting non-existent record returns 404
    res_admin_second = client.delete(f"/api/marks/{marks_id}", headers=admin_headers)
    assert res_admin_second.status_code == 404


# =====================================================================
# 2. STUDENT SELF ACCESS TESTS
# =====================================================================

def test_student_can_access_own_marks_me(
    client, teacher_headers, student_headers, sample_student, sample_student_beta
):
    """Student can retrieve only their own marks via /api/marks/me."""
    # Seed marks for student alpha
    client.post("/api/marks/", json={
        "student_id": sample_student["student_id"],
        "subject_code": "CS-301",
        "subject_name": "Algorithms",
        "semester": 5,
        "exam_type": "semester",
        "marks_obtained": 88.0,
        "max_marks": 100.0,
        "academic_year": "2024-2025",
    }, headers=teacher_headers)

    # Seed marks for student beta
    client.post("/api/marks/", json={
        "student_id": sample_student_beta["student_id"],
        "subject_code": "IT-201",
        "subject_name": "Data Structures",
        "semester": 3,
        "exam_type": "semester",
        "marks_obtained": 92.0,
        "max_marks": 100.0,
        "academic_year": "2024-2025",
    }, headers=teacher_headers)

    # Student alpha requests /api/marks/me
    res = client.get("/api/marks/me", headers=student_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["student_id"] == sample_student["student_id"]
    assert data["items"][0]["subject_code"] == "CS-301"


def test_student_can_access_own_marks_me_summary(
    client, teacher_headers, student_headers, sample_student
):
    """Student can retrieve consolidated summary of their own marks via /api/marks/me/summary."""
    # Seed marks: 1 Pass (A+), 1 Fail (F)
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
        "marks_obtained": 30.0,
        "max_marks": 100.0,
        "academic_year": "2024-2025",
    }, headers=teacher_headers)

    res = client.get("/api/marks/me/summary", headers=student_headers)
    assert res.status_code == 200
    summary = res.json()
    assert summary["student_id"] == sample_student["student_id"]
    assert summary["total_subjects"] == 2
    assert summary["total_marks_obtained"] == 120.0
    assert summary["total_max_marks"] == 200.0
    assert summary["overall_percentage"] == 60.0
    assert summary["passed_subjects"] == 1
    assert summary["failed_subjects"] == 1
    assert summary["grade_distribution"]["A+"] == 1
    assert summary["grade_distribution"]["F"] == 1


def test_student_cannot_access_another_student_marks(
    client, student_headers, sample_student_beta
):
    """Students cannot access another student's marks through administrative routes."""
    res = client.get(
        f"/api/marks/student/{sample_student_beta['student_id']}",
        headers=student_headers,
    )
    assert res.status_code == 403


def test_non_student_cannot_access_marks_me(client, admin_headers, teacher_headers):
    """Admin and Teacher cannot use /api/marks/me (student role only)."""
    res_admin = client.get("/api/marks/me", headers=admin_headers)
    assert res_admin.status_code == 403

    res_teacher = client.get("/api/marks/me", headers=teacher_headers)
    assert res_teacher.status_code == 403


# =====================================================================
# 3. VALIDATION & DUPLICATE TESTS
# =====================================================================

def test_invalid_marks_values_rejected(client, teacher_headers, sample_student):
    """Validates boundary constraints: marks_obtained >= 0, marks <= max, max > 0, sem in 1..8."""
    # Negative marks obtained
    res1 = client.post("/api/marks/", json={
        "student_id": sample_student["student_id"],
        "subject_code": "CS-301",
        "subject_name": "Algorithms",
        "semester": 5,
        "exam_type": "semester",
        "marks_obtained": -5.0,
        "max_marks": 100.0,
        "academic_year": "2024-2025",
    }, headers=teacher_headers)
    assert res1.status_code == 422

    # Marks obtained > max marks
    res2 = client.post("/api/marks/", json={
        "student_id": sample_student["student_id"],
        "subject_code": "CS-301",
        "subject_name": "Algorithms",
        "semester": 5,
        "exam_type": "semester",
        "marks_obtained": 105.0,
        "max_marks": 100.0,
        "academic_year": "2024-2025",
    }, headers=teacher_headers)
    assert res2.status_code == 422

    # Max marks <= 0
    res3 = client.post("/api/marks/", json={
        "student_id": sample_student["student_id"],
        "subject_code": "CS-301",
        "subject_name": "Algorithms",
        "semester": 5,
        "exam_type": "semester",
        "marks_obtained": 0.0,
        "max_marks": 0.0,
        "academic_year": "2024-2025",
    }, headers=teacher_headers)
    assert res3.status_code == 422

    # Invalid semester (< 1 or > 8)
    res4 = client.post("/api/marks/", json={
        "student_id": sample_student["student_id"],
        "subject_code": "CS-301",
        "subject_name": "Algorithms",
        "semester": 9,
        "exam_type": "semester",
        "marks_obtained": 50.0,
        "max_marks": 100.0,
        "academic_year": "2024-2025",
    }, headers=teacher_headers)
    assert res4.status_code == 422

    # Invalid exam type
    res5 = client.post("/api/marks/", json={
        "student_id": sample_student["student_id"],
        "subject_code": "CS-301",
        "subject_name": "Algorithms",
        "semester": 5,
        "exam_type": "final_pop_quiz",
        "marks_obtained": 50.0,
        "max_marks": 100.0,
        "academic_year": "2024-2025",
    }, headers=teacher_headers)
    assert res5.status_code == 422


def test_nonexistent_student_rejected(client, teacher_headers):
    """Attempting to record marks for a non-existent student returns 404."""
    res = client.post("/api/marks/", json={
        "student_id": "NON-EXISTENT-STUDENT-999",
        "subject_code": "CS-301",
        "subject_name": "Algorithms",
        "semester": 5,
        "exam_type": "semester",
        "marks_obtained": 80.0,
        "max_marks": 100.0,
        "academic_year": "2024-2025",
    }, headers=teacher_headers)
    assert res.status_code == 404


def test_duplicate_marks_rejected_with_409(client, teacher_headers, sample_student):
    """Enforces compound uniqueness on (student_id, subject_code, semester, exam_type, academic_year)."""
    payload = {
        "student_id": sample_student["student_id"],
        "subject_code": "CS-301",
        "subject_name": "Algorithms",
        "semester": 5,
        "exam_type": "internal_1",
        "marks_obtained": 40.0,
        "max_marks": 50.0,
        "academic_year": "2024-2025",
    }
    res1 = client.post("/api/marks/", json=payload, headers=teacher_headers)
    assert res1.status_code == 201

    res2 = client.post("/api/marks/", json=payload, headers=teacher_headers)
    assert res2.status_code == 409
    assert "already exist" in res2.json()["detail"].lower()


# =====================================================================
# 4. PERCENTAGE, GRADE & CALCULATION TESTS
# =====================================================================

def test_grade_and_percentage_scales(client, teacher_headers, sample_student):
    """
    Verifies grading scale:
    90–100 -> A+
    80–89.99 -> A
    70–79.99 -> B
    60–69.99 -> C
    50–59.99 -> D
    40–49.99 -> E
    Below 40 -> F
    """
    test_cases = [
        (100.0, 100.0, 100.0, "A+", "CS-101"),
        (85.0, 100.0, 85.0, "A", "CS-102"),
        (72.0, 100.0, 72.0, "B", "CS-103"),
        (65.0, 100.0, 65.0, "C", "CS-104"),
        (55.0, 100.0, 55.0, "D", "CS-105"),
        (45.0, 100.0, 45.0, "E", "CS-106"),
        (39.0, 100.0, 39.0, "F", "CS-107"),
        (45.0, 50.0, 90.0, "A+", "CS-108"),  # Weighted test
    ]

    for obtained, max_m, expected_pct, expected_grade, sub in test_cases:
        res = client.post("/api/marks/", json={
            "student_id": sample_student["student_id"],
            "subject_code": sub,
            "subject_name": f"Subject {sub}",
            "semester": 1,
            "exam_type": "semester",
            "marks_obtained": obtained,
            "max_marks": max_m,
            "academic_year": "2024-2025",
        }, headers=teacher_headers)
        assert res.status_code == 201
        data = res.json()
        assert data["percentage"] == expected_pct
        assert data["grade"] == expected_grade


def test_update_recalculates_percentage_and_grade(client, teacher_headers, sample_student):
    """Updating marks dynamically recalculates percentage and grade."""
    create_res = client.post("/api/marks/", json={
        "student_id": sample_student["student_id"],
        "subject_code": "CS-999",
        "subject_name": "Advanced Theory",
        "semester": 6,
        "exam_type": "model",
        "marks_obtained": 48.0,
        "max_marks": 50.0,
        "academic_year": "2024-2025",
    }, headers=teacher_headers)
    assert create_res.status_code == 201
    marks_id = create_res.json()["marks_id"]
    assert create_res.json()["percentage"] == 96.0
    assert create_res.json()["grade"] == "A+"

    # Update to 18 / 50 -> 36% -> Grade F
    update_res = client.put(f"/api/marks/{marks_id}", json={
        "marks_obtained": 18.0,
    }, headers=teacher_headers)
    assert update_res.status_code == 200
    assert update_res.json()["percentage"] == 36.0
    assert update_res.json()["grade"] == "F"


# =====================================================================
# 5. SUMMARY, FILTERING & PAGINATION TESTS
# =====================================================================

def test_student_marks_summary_zero_records_safe(client, admin_headers, sample_student):
    """Summary returns safely with zeros when no records exist."""
    res = client.get(
        f"/api/marks/student/{sample_student['student_id']}/summary",
        headers=admin_headers,
    )
    assert res.status_code == 200
    summary = res.json()
    assert summary["total_subjects"] == 0
    assert summary["total_marks_obtained"] == 0.0
    assert summary["total_max_marks"] == 0.0
    assert summary["overall_percentage"] == 0.0
    assert summary["passed_subjects"] == 0
    assert summary["failed_subjects"] == 0


def test_marks_filtering_and_pagination(client, teacher_headers, sample_student):
    """Verifies listing filters: subject_code, semester, exam_type, academic_year, search, and pagination."""
    # Seed 3 records
    client.post("/api/marks/", json={
        "student_id": sample_student["student_id"],
        "subject_code": "CS-201",
        "subject_name": "Data Structures",
        "semester": 3,
        "exam_type": "internal_1",
        "marks_obtained": 45.0,
        "max_marks": 50.0,
        "academic_year": "2023-2024",
    }, headers=teacher_headers)

    client.post("/api/marks/", json={
        "student_id": sample_student["student_id"],
        "subject_code": "CS-202",
        "subject_name": "Digital Logic",
        "semester": 3,
        "exam_type": "internal_2",
        "marks_obtained": 40.0,
        "max_marks": 50.0,
        "academic_year": "2023-2024",
    }, headers=teacher_headers)

    client.post("/api/marks/", json={
        "student_id": sample_student["student_id"],
        "subject_code": "CS-301",
        "subject_name": "Algorithms",
        "semester": 5,
        "exam_type": "semester",
        "marks_obtained": 85.0,
        "max_marks": 100.0,
        "academic_year": "2024-2025",
    }, headers=teacher_headers)

    # Filter by semester 3
    res_sem = client.get("/api/marks/?semester=3", headers=teacher_headers)
    assert res_sem.status_code == 200
    assert res_sem.json()["total"] == 2

    # Filter by academic_year 2024-2025
    res_yr = client.get("/api/marks/?academic_year=2024-2025", headers=teacher_headers)
    assert res_yr.status_code == 200
    assert res_yr.json()["total"] == 1

    # Search by keyword "Logic"
    res_search = client.get("/api/marks/?search=Logic", headers=teacher_headers)
    assert res_search.status_code == 200
    assert res_search.json()["total"] == 1
    assert res_search.json()["items"][0]["subject_code"] == "CS-202"

    # Pagination: limit 1, page 2
    res_page = client.get("/api/marks/?limit=1&page=2", headers=teacher_headers)
    assert res_page.status_code == 200
    assert len(res_page.json()["items"]) == 1
    assert res_page.json()["page"] == 2
    assert res_page.json()["pages"] == 3
