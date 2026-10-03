"""
Marks & Grades Service Module
Encapsulates business logic, database queries, calculations, uniqueness enforcement, and summaries for Marks records.
"""

from datetime import datetime, timezone
import logging
from typing import List, Optional, Tuple
import uuid
from bson import ObjectId
from fastapi import HTTPException, status
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from app.models.marks import (
    ExamType,
    MarksCreate,
    MarksInDB,
    MarksSummaryResponse,
    MarksUpdate,
    calculate_grade,
    calculate_percentage,
)
from app.services.student_service import get_student_by_identifier

logger = logging.getLogger("edumanage.services.marks")


def get_marks_by_id(db: Database, identifier: str) -> Optional[MarksInDB]:
    """
    Finds a marks record in MongoDB by marks_id or BSON _id.
    """
    trimmed = identifier.strip()
    doc = db.marks.find_one({"marks_id": trimmed})
    if not doc and ObjectId.is_valid(trimmed):
        doc = db.marks.find_one({"_id": ObjectId(trimmed)})

    if doc:
        return MarksInDB.model_validate(doc)
    return None


def create_marks(
    db: Database,
    marks_in: MarksCreate,
    entered_by: str,
) -> MarksInDB:
    """
    Creates and persists a new marks document.
    Validates student existence, enforces unique assessment constraints, calculates percentage and grade.
    """
    student_identifier = marks_in.student_id.strip()
    student = get_student_by_identifier(db=db, identifier=student_identifier)
    if not student:
        logger.warning("Marks creation rejected: Student '%s' not found", student_identifier)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with identifier '{student_identifier}' was not found.",
        )

    canonical_student_id = student.student_id
    subject_code = marks_in.subject_code.strip().upper()
    semester = marks_in.semester
    exam_type_val = (
        marks_in.exam_type.value
        if hasattr(marks_in.exam_type, "value")
        else str(marks_in.exam_type).lower()
    )
    academic_year = marks_in.academic_year.strip()

    # Pre-check duplicate marks for same student, subject, semester, exam_type, and academic_year
    existing_record = db.marks.find_one({
        "student_id": canonical_student_id,
        "subject_code": subject_code,
        "semester": semester,
        "exam_type": exam_type_val,
        "academic_year": academic_year,
    })
    if existing_record:
        logger.warning(
            "Duplicate marks creation attempt for student '%s', subject '%s', semester %d, exam '%s', year '%s'",
            canonical_student_id,
            subject_code,
            semester,
            exam_type_val,
            academic_year,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Marks already exist for this student, subject, semester, exam type, and academic year.",
        )

    # Server-side percentage and grade calculation
    percentage = calculate_percentage(marks_in.marks_obtained, marks_in.max_marks)
    grade = calculate_grade(percentage)

    # Generate custom marks identifier if not supplied
    marks_id = (
        marks_in.marks_id.strip()
        if marks_in.marks_id and marks_in.marks_id.strip()
        else f"MRK-{uuid.uuid4().hex[:10].upper()}"
    )

    if db.marks.find_one({"marks_id": marks_id}):
        marks_id = f"MRK-{uuid.uuid4().hex[:10].upper()}"

    now = datetime.now(timezone.utc)
    marks_db = MarksInDB(
        marks_id=marks_id,
        student_id=canonical_student_id,
        subject_code=subject_code,
        subject_name=marks_in.subject_name.strip(),
        semester=semester,
        exam_type=marks_in.exam_type,
        marks_obtained=marks_in.marks_obtained,
        max_marks=marks_in.max_marks,
        percentage=percentage,
        grade=grade,
        academic_year=academic_year,
        remarks=marks_in.remarks.strip() if marks_in.remarks else None,
        entered_by=entered_by.strip(),
        created_at=now,
        updated_at=now,
    )

    marks_dict = marks_db.model_dump(by_alias=True)

    try:
        db.marks.insert_one(marks_dict)
        logger.info(
            "Recorded marks %s for student %s in %s (Semester %d, %s): %s/%s -> %s%% (Grade %s)",
            marks_id,
            canonical_student_id,
            subject_code,
            semester,
            exam_type_val,
            marks_in.marks_obtained,
            marks_in.max_marks,
            percentage,
            grade,
        )
        return marks_db
    except DuplicateKeyError as exc:
        logger.warning("DuplicateKeyError on marks insert: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Marks already exist for this student, subject, semester, exam type, and academic year.",
        ) from exc


def get_marks_list(
    db: Database,
    page: int = 1,
    limit: int = 20,
    student_id: Optional[str] = None,
    subject_code: Optional[str] = None,
    semester: Optional[int] = None,
    exam_type: Optional[str] = None,
    academic_year: Optional[str] = None,
    search: Optional[str] = None,
) -> Tuple[List[MarksInDB], int, int]:
    """
    Retrieves paginated marks records supporting multi-parameter filters and search.
    Returns (items, total_count, total_pages).
    """
    page_num = max(1, page)
    page_limit = min(max(1, limit), 100)
    skip = (page_num - 1) * page_limit

    filter_query = {}

    if student_id and student_id.strip():
        target_student = get_student_by_identifier(db, student_id.strip())
        canonical_id = target_student.student_id if target_student else student_id.strip()
        filter_query["student_id"] = canonical_id

    if subject_code and subject_code.strip():
        filter_query["subject_code"] = subject_code.strip().upper()

    if semester is not None:
        filter_query["semester"] = semester

    if exam_type and exam_type.strip():
        filter_query["exam_type"] = exam_type.strip().lower()

    if academic_year and academic_year.strip():
        filter_query["academic_year"] = academic_year.strip()

    if search and search.strip():
        term = search.strip()
        filter_query["$or"] = [
            {"subject_name": {"$regex": term, "$options": "i"}},
            {"subject_code": {"$regex": term, "$options": "i"}},
            {"student_id": {"$regex": term, "$options": "i"}},
            {"marks_id": {"$regex": term, "$options": "i"}},
        ]

    total = db.marks.count_documents(filter_query)
    pages = (total + page_limit - 1) // page_limit if total > 0 else 0

    cursor = (
        db.marks.find(filter_query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(page_limit)
    )

    items = [MarksInDB.model_validate(doc) for doc in cursor]
    return items, total, pages


def get_student_marks(
    db: Database,
    student_id: str,
    page: int = 1,
    limit: int = 20,
    semester: Optional[int] = None,
    exam_type: Optional[str] = None,
    academic_year: Optional[str] = None,
) -> Tuple[List[MarksInDB], int, int]:
    """
    Fetches paginated marks records for a specific verified student.
    """
    target_student = get_student_by_identifier(db, student_id.strip())
    if not target_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with identifier '{student_id}' was not found.",
        )

    return get_marks_list(
        db=db,
        page=page,
        limit=limit,
        student_id=target_student.student_id,
        semester=semester,
        exam_type=exam_type,
        academic_year=academic_year,
    )


def update_marks(
    db: Database,
    identifier: str,
    marks_update: MarksUpdate,
) -> Optional[MarksInDB]:
    """
    Updates marks attributes and recalculates percentage and grade.
    """
    existing = get_marks_by_id(db, identifier)
    if not existing:
        return None

    update_dict = marks_update.model_dump(exclude_unset=True)
    if not update_dict:
        return existing

    # Normalize exam_type if updated
    if "exam_type" in update_dict and update_dict["exam_type"] is not None:
        val = update_dict["exam_type"]
        update_dict["exam_type"] = val.value if hasattr(val, "value") else str(val).lower()

    if "subject_code" in update_dict and update_dict["subject_code"] is not None:
        update_dict["subject_code"] = update_dict["subject_code"].strip().upper()

    if "academic_year" in update_dict and update_dict["academic_year"] is not None:
        update_dict["academic_year"] = update_dict["academic_year"].strip()

    # Determine resulting score values and validate bounds
    target_marks = update_dict.get("marks_obtained", existing.marks_obtained)
    target_max = update_dict.get("max_marks", existing.max_marks)

    if target_marks > target_max:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"marks_obtained ({target_marks}) cannot be greater than max_marks ({target_max}).",
        )

    # Server-side recalculation of percentage and grade
    new_percentage = calculate_percentage(target_marks, target_max)
    new_grade = calculate_grade(new_percentage)

    update_dict["percentage"] = new_percentage
    update_dict["grade"] = new_grade

    # Uniqueness conflict check if any key dimension changes
    target_subject_code = update_dict.get("subject_code", existing.subject_code)
    target_semester = update_dict.get("semester", existing.semester)
    target_exam_type = update_dict.get("exam_type", existing.exam_type)
    target_academic_year = update_dict.get("academic_year", existing.academic_year)

    conflict = db.marks.find_one({
        "student_id": existing.student_id,
        "subject_code": target_subject_code,
        "semester": target_semester,
        "exam_type": target_exam_type,
        "academic_year": target_academic_year,
        "_id": {"$ne": existing.id},
    })
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Marks already exist for this student, subject, semester, exam type, and academic year.",
        )

    update_dict["updated_at"] = datetime.now(timezone.utc)

    try:
        db.marks.update_one({"_id": existing.id}, {"$set": update_dict})
        updated_doc = db.marks.find_one({"_id": existing.id})
        return MarksInDB.model_validate(updated_doc)
    except DuplicateKeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Marks already exist for this student, subject, semester, exam type, and academic year.",
        ) from exc


def delete_marks(db: Database, identifier: str) -> Optional[MarksInDB]:
    """
    Permanently removes a marks record. Restricted to Admins.
    """
    existing = get_marks_by_id(db, identifier)
    if not existing:
        return None

    db.marks.delete_one({"_id": existing.id})
    logger.info("Deleted marks record: %s", existing.marks_id)
    return existing


def calculate_student_marks_summary(
    db: Database,
    student_id: str,
    semester: Optional[int] = None,
    academic_year: Optional[str] = None,
) -> MarksSummaryResponse:
    """
    Calculates consolidated marks performance summary metrics for a student.
    Handles zero-assessment cases safely.
    """
    target_student = get_student_by_identifier(db, student_id.strip())
    if not target_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with identifier '{student_id}' was not found.",
        )

    canonical_id = target_student.student_id

    filter_query = {"student_id": canonical_id}
    if semester is not None:
        filter_query["semester"] = semester
    if academic_year and academic_year.strip():
        filter_query["academic_year"] = academic_year.strip()

    records_cursor = db.marks.find(filter_query)
    records = [MarksInDB.model_validate(doc) for doc in records_cursor]

    total_subjects = len(records)
    total_marks_obtained = round(sum(r.marks_obtained for r in records), 2)
    total_max_marks = round(sum(r.max_marks for r in records), 2)

    overall_percentage = (
        round((total_marks_obtained / total_max_marks) * 100.0, 2)
        if total_max_marks > 0
        else 0.0
    )

    passed_subjects = sum(1 for r in records if r.percentage >= 40.0)
    failed_subjects = sum(1 for r in records if r.percentage < 40.0)

    grade_distribution = {
        "A+": 0,
        "A": 0,
        "B": 0,
        "C": 0,
        "D": 0,
        "E": 0,
        "F": 0,
    }

    for r in records:
        if r.grade in grade_distribution:
            grade_distribution[r.grade] += 1
        else:
            grade_distribution[r.grade] = 1

    return MarksSummaryResponse(
        student_id=canonical_id,
        total_subjects=total_subjects,
        total_marks_obtained=total_marks_obtained,
        total_max_marks=total_max_marks,
        overall_percentage=overall_percentage,
        passed_subjects=passed_subjects,
        failed_subjects=failed_subjects,
        grade_distribution=grade_distribution,
    )
