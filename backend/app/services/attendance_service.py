"""
Attendance Service Module
Encapsulates business logic, database queries, summaries, and uniqueness validation for Attendance records.
"""

from datetime import datetime, timezone
import logging
from typing import List, Optional, Tuple, Union
import uuid
from bson import ObjectId
from fastapi import HTTPException, status
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from app.models.attendance import (
    AttendanceCreate,
    AttendanceInDB,
    AttendanceStatus,
    AttendanceSummaryResponse,
    AttendanceUpdate,
)
from app.services.student_service import get_student_by_identifier

logger = logging.getLogger("edumanage.services.attendance")


def get_attendance_by_id(db: Database, identifier: str) -> Optional[AttendanceInDB]:
    """
    Finds an attendance record in MongoDB by custom attendance_id or BSON _id.
    """
    trimmed = identifier.strip()
    doc = db.attendance.find_one({"attendance_id": trimmed})
    if not doc and ObjectId.is_valid(trimmed):
        doc = db.attendance.find_one({"_id": ObjectId(trimmed)})

    if doc:
        return AttendanceInDB.model_validate(doc)
    return None


def create_attendance(
    db: Database,
    attendance_in: AttendanceCreate,
    marked_by: str,
) -> AttendanceInDB:
    """
    Creates and persists a new attendance document.
    Validates student existence and ensures a student cannot have duplicate attendance for the same date.
    """
    student_identifier = attendance_in.student_id.strip()
    student = get_student_by_identifier(db=db, identifier=student_identifier)
    if not student:
        logger.warning("Attendance creation rejected: Student '%s' not found", student_identifier)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with identifier '{student_identifier}' was not found.",
        )

    # Standardize on student's institutional student_id
    canonical_student_id = student.student_id
    session_date = attendance_in.date.strip()

    # Pre-check duplicate attendance for same student and date
    existing_record = db.attendance.find_one({
        "student_id": canonical_student_id,
        "date": session_date,
    })
    if existing_record:
        logger.warning(
            "Duplicate attendance creation attempt for student '%s' on date '%s'",
            canonical_student_id,
            session_date,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Attendance record for student '{canonical_student_id}' on date '{session_date}' already exists.",
        )

    # Generate custom attendance identifier if not provided
    attendance_id = (
        attendance_in.attendance_id.strip()
        if attendance_in.attendance_id and attendance_in.attendance_id.strip()
        else f"ATT-{uuid.uuid4().hex[:10].upper()}"
    )

    # Pre-check attendance_id uniqueness
    if db.attendance.find_one({"attendance_id": attendance_id}):
        attendance_id = f"ATT-{uuid.uuid4().hex[:10].upper()}"

    now = datetime.now(timezone.utc)
    attendance_db = AttendanceInDB(
        attendance_id=attendance_id,
        student_id=canonical_student_id,
        date=session_date,
        status=attendance_in.status,
        remarks=attendance_in.remarks.strip() if attendance_in.remarks else None,
        marked_by=marked_by.strip(),
        created_at=now,
        updated_at=now,
    )

    attendance_dict = attendance_db.model_dump(by_alias=True)

    try:
        db.attendance.insert_one(attendance_dict)
        logger.info(
            "Recorded attendance: %s for student %s on %s (status: %s)",
            attendance_id,
            canonical_student_id,
            session_date,
            attendance_in.status,
        )
        return attendance_db
    except DuplicateKeyError as exc:
        logger.warning("DuplicateKeyError on attendance insert: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Attendance record for student '{canonical_student_id}' on date '{session_date}' already exists.",
        ) from exc


def get_attendance_list(
    db: Database,
    page: int = 1,
    limit: int = 20,
    student_id: Optional[str] = None,
    date: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
) -> Tuple[List[AttendanceInDB], int, int]:
    """
    Retrieves paginated attendance records supporting multi-parameter filters.
    Returns (items, total_count, total_pages).
    """
    page_num = max(1, page)
    page_limit = min(max(1, limit), 100)
    skip = (page_num - 1) * page_limit

    filter_query = {}

    if student_id and student_id.strip():
        # Check if student_id matches a student identifier
        target_student = get_student_by_identifier(db, student_id.strip())
        canonical_id = target_student.student_id if target_student else student_id.strip()
        filter_query["student_id"] = canonical_id

    if date and date.strip():
        filter_query["date"] = date.strip()
    elif start_date or end_date:
        date_query = {}
        if start_date and start_date.strip():
            date_query["$gte"] = start_date.strip()
        if end_date and end_date.strip():
            date_query["$lte"] = end_date.strip()
        if date_query:
            filter_query["date"] = date_query

    if status and status.strip():
        filter_query["status"] = status.strip().lower()

    total = db.attendance.count_documents(filter_query)
    pages = (total + page_limit - 1) // page_limit if total > 0 else 0

    cursor = (
        db.attendance.find(filter_query)
        .sort("date", -1)
        .skip(skip)
        .limit(page_limit)
    )

    items = [AttendanceInDB.model_validate(doc) for doc in cursor]
    return items, total, pages


def get_student_attendance(
    db: Database,
    student_id: str,
    page: int = 1,
    limit: int = 20,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
) -> Tuple[List[AttendanceInDB], int, int]:
    """
    Fetches paginated attendance records for a specific verified student.
    """
    target_student = get_student_by_identifier(db, student_id.strip())
    if not target_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with identifier '{student_id}' was not found.",
        )

    return get_attendance_list(
        db=db,
        page=page,
        limit=limit,
        student_id=target_student.student_id,
        start_date=start_date,
        end_date=end_date,
        status=status,
    )


def update_attendance(
    db: Database,
    identifier: str,
    attendance_update: AttendanceUpdate,
) -> Optional[AttendanceInDB]:
    """
    Updates status, remarks, or date for an existing attendance record.
    """
    existing = get_attendance_by_id(db, identifier)
    if not existing:
        return None

    update_dict = attendance_update.model_dump(exclude_unset=True)
    if not update_dict:
        return existing

    # Handle status enum conversion to string value
    if "status" in update_dict and update_dict["status"] is not None:
        val = update_dict["status"]
        update_dict["status"] = val.value if hasattr(val, "value") else str(val).lower()

    # Pre-check duplicate conflict if date changed
    if "date" in update_dict and update_dict["date"] != existing.date:
        conflict = db.attendance.find_one({
            "student_id": existing.student_id,
            "date": update_dict["date"],
            "_id": {"$ne": existing.id},
        })
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Attendance record for student '{existing.student_id}' on date '{update_dict['date']}' already exists.",
            )

    update_dict["updated_at"] = datetime.now(timezone.utc)

    try:
        db.attendance.update_one({"_id": existing.id}, {"$set": update_dict})
        updated_doc = db.attendance.find_one({"_id": existing.id})
        return AttendanceInDB.model_validate(updated_doc)
    except DuplicateKeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Attendance record with this student_id and date already exists.",
        ) from exc


def delete_attendance(db: Database, identifier: str) -> Optional[AttendanceInDB]:
    """
    Permanently deletes an attendance record. Restricted to Admins.
    """
    existing = get_attendance_by_id(db, identifier)
    if not existing:
        return None

    db.attendance.delete_one({"_id": existing.id})
    logger.info("Deleted attendance record: %s", existing.attendance_id)
    return existing


def calculate_attendance_summary(
    db: Database,
    student_id: str,
) -> AttendanceSummaryResponse:
    """
    Calculates consolidated attendance summary metrics for a student.
    Returns counts for present, absent, late, excused, and attendance percentage.
    Safely handles zero-record cases.
    """
    target_student = get_student_by_identifier(db, student_id.strip())
    if not target_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with identifier '{student_id}' was not found.",
        )

    canonical_id = target_student.student_id

    records_cursor = db.attendance.find({"student_id": canonical_id})
    records = [AttendanceInDB.model_validate(doc) for doc in records_cursor]

    total_days = len(records)
    present_days = sum(1 for r in records if r.status in [AttendanceStatus.PRESENT, "present"])
    absent_days = sum(1 for r in records if r.status in [AttendanceStatus.ABSENT, "absent"])
    late_days = sum(1 for r in records if r.status in [AttendanceStatus.LATE, "late"])
    excused_days = sum(1 for r in records if r.status in [AttendanceStatus.EXCUSED, "excused"])

    attendance_percentage = (
        round((present_days / total_days) * 100.0, 2)
        if total_days > 0
        else 0.0
    )

    return AttendanceSummaryResponse(
        student_id=canonical_id,
        total_days=total_days,
        present_days=present_days,
        absent_days=absent_days,
        late_days=late_days,
        excused_days=excused_days,
        attendance_percentage=attendance_percentage,
    )
