"""
Seed Initial Demo Users & Student Records into MongoDB Atlas
Creates default Administrator, Faculty, and Student accounts for instant login.
"""

from datetime import datetime, timezone
import logging
from pymongo.database import Database

from app.core.security import get_password_hash
from app.db.mongodb import db_manager
from app.models.user import UserRole

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("edumanage.db.seed")

DEMO_USERS = [
    {
        "full_name": "Sarah Jenkins",
        "email": "sarah.jenkins@edumanage.edu",
        "role": UserRole.ADMIN.value,
        "password": "AdminSecret123!",
    },
    {
        "full_name": "Marcus Vance",
        "email": "marcus.vance@edumanage.edu",
        "role": UserRole.TEACHER.value,
        "password": "TeacherSecret123!",
    },
    {
        "full_name": "Arun Kumar",
        "email": "arun.kumar@student.edumanage.edu",
        "role": UserRole.STUDENT.value,
        "password": "StudentSecret123!",
    },
]

DEMO_STUDENTS = [
    {
        "student_id": "STU-2026-001",
        "roll_number": "CS-22-089",
        "full_name": "Arun Kumar",
        "email": "arun.kumar@student.edumanage.edu",
        "department": "Computer Science",
        "year": 3,
        "section": "A",
        "phone": "+1 (555) 234-5678",
        "address": "402 Campus Residence, Sector 4",
        "is_active": True,
    },
]


def seed_database(db: Database) -> None:
    now = datetime.now(timezone.utc)

    # 1. Seed Users
    for user_info in DEMO_USERS:
        email = user_info["email"].lower().strip()
        existing = db.users.find_one({"email": email})
        if not existing:
            hashed = get_password_hash(user_info["password"])
            db.users.insert_one({
                "full_name": user_info["full_name"],
                "email": email,
                "hashed_password": hashed,
                "role": user_info["role"],
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            })
            logger.info("Created user: %s (Role: %s)", email, user_info["role"])
        else:
            logger.info("User already exists: %s", email)

    # 2. Seed Students
    for s_info in DEMO_STUDENTS:
        existing_s = db.students.find_one({"email": s_info["email"].lower().strip()})
        if not existing_s:
            doc = {**s_info, "created_at": now, "updated_at": now}
            db.students.insert_one(doc)
            logger.info("Created student record: %s (%s)", s_info["student_id"], s_info["full_name"])
        else:
            logger.info("Student already exists: %s", s_info["student_id"])

    # 3. Seed Initial Attendance
    demo_att = [
        {"attendance_id": "ATT-DEMO-001", "student_id": "STU-2026-001", "date": "2026-10-01", "status": "present", "remarks": "Regular session", "marked_by": "Marcus Vance", "created_at": now, "updated_at": now},
        {"attendance_id": "ATT-DEMO-002", "student_id": "STU-2026-001", "date": "2026-10-02", "status": "present", "remarks": "Algorithms lecture", "marked_by": "Marcus Vance", "created_at": now, "updated_at": now},
    ]
    for att in demo_att:
        if not db.attendance.find_one({"attendance_id": att["attendance_id"]}):
            db.attendance.insert_one(att)
            logger.info("Created demo attendance: %s", att["attendance_id"])

    # 4. Seed Initial Marks
    demo_marks = [
        {
            "marks_id": "MRK-DEMO-001",
            "student_id": "STU-2026-001",
            "subject_code": "CS-301",
            "subject_name": "Design & Analysis of Algorithms",
            "semester": 6,
            "exam_type": "semester",
            "marks_obtained": 88.0,
            "max_marks": 100.0,
            "percentage": 88.0,
            "grade": "A+",
            "academic_year": "2024-2025",
            "remarks": "Excellent analysis",
            "entered_by": "Marcus Vance",
            "created_at": now,
            "updated_at": now,
        },
        {
            "marks_id": "MRK-DEMO-002",
            "student_id": "STU-2026-001",
            "subject_code": "CS-302",
            "subject_name": "Database Management Systems",
            "semester": 6,
            "exam_type": "semester",
            "marks_obtained": 82.0,
            "max_marks": 100.0,
            "percentage": 82.0,
            "grade": "A",
            "academic_year": "2024-2025",
            "remarks": "Strong SQL proficiency",
            "entered_by": "Marcus Vance",
            "created_at": now,
            "updated_at": now,
        },
    ]
    for mrk in demo_marks:
        if not db.marks.find_one({"marks_id": mrk["marks_id"]}):
            db.marks.insert_one(mrk)
            logger.info("Created demo marks: %s", mrk["marks_id"])


if __name__ == "__main__":
    logger.info("Connecting to MongoDB to seed demo data...")
    if db_manager.connect():
        seed_database(db_manager.db)
        logger.info("Demo database seeding complete!")
    else:
        logger.error("Failed to connect to MongoDB.")
