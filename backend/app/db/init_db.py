"""
Database Initialization Module
Handles creation of MongoDB collections, unique indexes, and initial configuration.
"""

import logging
import pymongo
from pymongo.database import Database

logger = logging.getLogger("edumanage.db.init")


def init_db(db: Database) -> None:
    """
    Initializes required MongoDB indexes and constraints for EduManage collections:
    - users: unique on email
    - students: unique on student_id, email, roll_number
    - attendance: unique on attendance_id, compound unique on student_id + date, indexes on date, marked_by, status
    """
    if db is None:
        logger.warning("Cannot initialize indexes: database handle is None.")
        return

    try:
        # Create unique index on users.email
        logger.info("Ensuring unique index on 'users.email'...")
        db.users.create_index(
            [("email", pymongo.ASCENDING)],
            unique=True,
            name="idx_users_email_unique",
            background=True,
        )

        # Create unique indexes on students collection
        logger.info("Ensuring unique indexes on 'students' collection...")
        db.students.create_index(
            [("student_id", pymongo.ASCENDING)],
            unique=True,
            name="idx_students_student_id_unique",
            background=True,
        )
        db.students.create_index(
            [("email", pymongo.ASCENDING)],
            unique=True,
            name="idx_students_email_unique",
            background=True,
        )
        db.students.create_index(
            [("roll_number", pymongo.ASCENDING)],
            unique=True,
            name="idx_students_roll_number_unique",
            background=True,
        )

        # Create indexes on attendance collection
        logger.info("Ensuring indexes on 'attendance' collection...")
        db.attendance.create_index(
            [("attendance_id", pymongo.ASCENDING)],
            unique=True,
            name="idx_attendance_attendance_id_unique",
            background=True,
        )
        db.attendance.create_index(
            [("student_id", pymongo.ASCENDING), ("date", pymongo.ASCENDING)],
            unique=True,
            name="idx_attendance_student_date_unique",
            background=True,
        )
        db.attendance.create_index(
            [("student_id", pymongo.ASCENDING)],
            name="idx_attendance_student_id",
            background=True,
        )
        db.attendance.create_index(
            [("date", pymongo.ASCENDING)],
            name="idx_attendance_date",
            background=True,
        )
        db.attendance.create_index(
            [("marked_by", pymongo.ASCENDING)],
            name="idx_attendance_marked_by",
            background=True,
        )
        db.attendance.create_index(
            [("status", pymongo.ASCENDING)],
            name="idx_attendance_status",
            background=True,
        )

        # Create indexes on marks collection
        logger.info("Ensuring indexes on 'marks' collection...")
        db.marks.create_index(
            [("marks_id", pymongo.ASCENDING)],
            unique=True,
            name="idx_marks_marks_id_unique",
            background=True,
        )
        db.marks.create_index(
            [
                ("student_id", pymongo.ASCENDING),
                ("subject_code", pymongo.ASCENDING),
                ("semester", pymongo.ASCENDING),
                ("exam_type", pymongo.ASCENDING),
                ("academic_year", pymongo.ASCENDING),
            ],
            unique=True,
            name="idx_marks_student_subject_sem_exam_year_unique",
            background=True,
        )
        db.marks.create_index(
            [("student_id", pymongo.ASCENDING)],
            name="idx_marks_student_id",
            background=True,
        )
        db.marks.create_index(
            [("subject_code", pymongo.ASCENDING)],
            name="idx_marks_subject_code",
            background=True,
        )
        db.marks.create_index(
            [("semester", pymongo.ASCENDING)],
            name="idx_marks_semester",
            background=True,
        )
        db.marks.create_index(
            [("exam_type", pymongo.ASCENDING)],
            name="idx_marks_exam_type",
            background=True,
        )
        db.marks.create_index(
            [("academic_year", pymongo.ASCENDING)],
            name="idx_marks_academic_year",
            background=True,
        )
        db.marks.create_index(
            [("entered_by", pymongo.ASCENDING)],
            name="idx_marks_entered_by",
            background=True,
        )

        logger.info("Database indexes initialized successfully.")
    except Exception as exc:
        logger.error("Failed to initialize database indexes: %s", exc)
