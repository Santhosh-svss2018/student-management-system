"""
Reports Service Module
Generates filtered institutional reports and CSV/PDF export streams from MongoDB.
"""

import csv
from datetime import datetime, timezone
import io
import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from fastapi import HTTPException, status
from pymongo.database import Database

from app.models.reports import (
    AcademicSummaryMetrics,
    AcademicSummaryReportResponse,
    AttendanceReportItem,
    AttendanceReportResponse,
    MarksReportItem,
    MarksReportResponse,
    StudentReportItem,
    StudentReportResponse,
)
from app.services.ai_insights_service import calculate_student_risk
from app.services.attendance_service import calculate_attendance_summary
from app.services.marks_service import calculate_student_marks_summary
from app.services.student_service import get_student_by_identifier

logger = logging.getLogger("edumanage.services.reports")


def get_students_report(
    db: Database,
    department: Optional[str] = None,
    year: Optional[int] = None,
    section: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> StudentReportResponse:
    """
    Fetches filtered, paginated student report records with live academic metrics.
    """
    page_num = max(1, page)
    page_limit = min(max(1, limit), 500)
    skip = (page_num - 1) * page_limit

    filter_query: Dict[str, Any] = {}

    if department and department.strip() and department != "All Departments" and department != "All":
        filter_query["department"] = department.strip()

    if year is not None:
        filter_query["year"] = int(year)

    if section and section.strip() and section != "All":
        filter_query["section"] = section.strip().upper()

    if is_active is not None:
        filter_query["is_active"] = bool(is_active)

    if search and search.strip():
        search_escaped = re.escape(search.strip())
        regex_pattern = {"$regex": search_escaped, "$options": "i"}
        filter_query["$or"] = [
            {"full_name": regex_pattern},
            {"email": regex_pattern},
            {"student_id": regex_pattern},
            {"roll_number": regex_pattern},
            {"department": regex_pattern},
        ]

    total = db.students.count_documents(filter_query)
    pages = (total + page_limit - 1) // page_limit if total > 0 else 0

    cursor = (
        db.students.find(filter_query)
        .sort("student_id", 1)
        .skip(skip)
        .limit(page_limit)
    )

    items: List[StudentReportItem] = []
    for doc in cursor:
        sid = doc.get("student_id", "")
        att_pct = 0.0
        acad_pct = 0.0
        risk_lvl = "LOW"

        if sid:
            try:
                att_sum = calculate_attendance_summary(db, sid)
                att_pct = att_sum.attendance_percentage
            except Exception:
                pass

            try:
                mrk_sum = calculate_student_marks_summary(db, sid)
                acad_pct = mrk_sum.overall_percentage
            except Exception:
                pass

            try:
                r_sum = calculate_student_risk(db, sid)
                risk_lvl = r_sum.risk_level.value
            except Exception:
                pass

        items.append(
            StudentReportItem(
                student_id=sid,
                roll_number=doc.get("roll_number", ""),
                full_name=doc.get("full_name", "Student"),
                email=doc.get("email", ""),
                department=doc.get("department", "Unassigned"),
                year=int(doc.get("year", 1)),
                section=doc.get("section", "A"),
                attendance_percentage=att_pct,
                academic_percentage=acad_pct,
                risk_level=risk_lvl,
                is_active=bool(doc.get("is_active", True)),
            )
        )

    return StudentReportResponse(
        items=items,
        total=total,
        page=page_num,
        pages=pages,
        limit=page_limit,
    )


def get_attendance_report(
    db: Database,
    department: Optional[str] = None,
    year: Optional[int] = None,
    section: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    student_id: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> AttendanceReportResponse:
    """
    Fetches filtered, paginated attendance report items enriched with student metadata.
    """
    page_num = max(1, page)
    page_limit = min(max(1, limit), 500)
    skip = (page_num - 1) * page_limit

    # First filter students by department/year/section if provided
    student_filters: Dict[str, Any] = {}
    if department and department.strip() and department != "All Departments" and department != "All":
        student_filters["department"] = department.strip()
    if year is not None:
        student_filters["year"] = int(year)
    if section and section.strip() and section != "All":
        student_filters["section"] = section.strip().upper()

    target_student_ids = None
    if student_filters:
        target_student_ids = [
            s.get("student_id") for s in db.students.find(student_filters) if s.get("student_id")
        ]

    filter_query: Dict[str, Any] = {}

    if student_id and student_id.strip():
        canonical_student = get_student_by_identifier(db, student_id.strip())
        canonical_id = canonical_student.student_id if canonical_student else student_id.strip()
        filter_query["student_id"] = canonical_id
    elif target_student_ids is not None:
        filter_query["student_id"] = {"$in": target_student_ids}

    if date_from or date_to:
        date_query: Dict[str, str] = {}
        if date_from and date_from.strip():
            date_query["$gte"] = date_from.strip()
        if date_to and date_to.strip():
            date_query["$lte"] = date_to.strip()
        if date_query:
            filter_query["date"] = date_query

    if status and status.strip() and status.lower() != "all":
        filter_query["status"] = status.strip().lower()

    total = db.attendance.count_documents(filter_query)
    pages = (total + page_limit - 1) // page_limit if total > 0 else 0

    cursor = (
        db.attendance.find(filter_query)
        .sort("date", -1)
        .skip(skip)
        .limit(page_limit)
    )

    items: List[AttendanceReportItem] = []
    # Cache student lookups to avoid repeated database hits
    student_cache: Dict[str, Dict[str, Any]] = {}

    for doc in cursor:
        sid = doc.get("student_id", "")
        if sid not in student_cache:
            st = db.students.find_one({"student_id": sid})
            student_cache[sid] = st if st else {}

        s_info = student_cache[sid]
        items.append(
            AttendanceReportItem(
                attendance_id=doc.get("attendance_id", ""),
                student_id=sid,
                student_name=s_info.get("full_name", "Student"),
                roll_number=s_info.get("roll_number", sid),
                department=s_info.get("department", "Unassigned"),
                date=doc.get("date", ""),
                status=doc.get("status", "present"),
                remarks=doc.get("remarks"),
                marked_by=doc.get("marked_by", "system"),
            )
        )

    return AttendanceReportResponse(
        items=items,
        total=total,
        page=page_num,
        pages=pages,
        limit=page_limit,
    )


def get_marks_report(
    db: Database,
    department: Optional[str] = None,
    semester: Optional[int] = None,
    subject_code: Optional[str] = None,
    exam_type: Optional[str] = None,
    academic_year: Optional[str] = None,
    student_id: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> MarksReportResponse:
    """
    Fetches filtered, paginated marks report items enriched with student metadata.
    """
    page_num = max(1, page)
    page_limit = min(max(1, limit), 500)
    skip = (page_num - 1) * page_limit

    student_filters: Dict[str, Any] = {}
    if department and department.strip() and department != "All Departments" and department != "All":
        student_filters["department"] = department.strip()

    target_student_ids = None
    if student_filters:
        target_student_ids = [
            s.get("student_id") for s in db.students.find(student_filters) if s.get("student_id")
        ]

    filter_query: Dict[str, Any] = {}

    if student_id and student_id.strip():
        canonical_student = get_student_by_identifier(db, student_id.strip())
        canonical_id = canonical_student.student_id if canonical_student else student_id.strip()
        filter_query["student_id"] = canonical_id
    elif target_student_ids is not None:
        filter_query["student_id"] = {"$in": target_student_ids}

    if semester is not None:
        filter_query["semester"] = int(semester)

    if subject_code and subject_code.strip() and subject_code != "All":
        filter_query["subject_code"] = subject_code.strip().upper()

    if exam_type and exam_type.strip() and exam_type.lower() != "all":
        filter_query["exam_type"] = exam_type.strip().lower()

    if academic_year and academic_year.strip() and academic_year != "All":
        filter_query["academic_year"] = academic_year.strip()

    total = db.marks.count_documents(filter_query)
    pages = (total + page_limit - 1) // page_limit if total > 0 else 0

    cursor = (
        db.marks.find(filter_query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(page_limit)
    )

    items: List[MarksReportItem] = []
    student_cache: Dict[str, Dict[str, Any]] = {}

    for doc in cursor:
        sid = doc.get("student_id", "")
        if sid not in student_cache:
            st = db.students.find_one({"student_id": sid})
            student_cache[sid] = st if st else {}

        s_info = student_cache[sid]
        items.append(
            MarksReportItem(
                marks_id=doc.get("marks_id", ""),
                student_id=sid,
                student_name=s_info.get("full_name", "Student"),
                roll_number=s_info.get("roll_number", sid),
                department=s_info.get("department", "Unassigned"),
                subject_code=doc.get("subject_code", ""),
                subject_name=doc.get("subject_name", ""),
                semester=int(doc.get("semester", 1)),
                exam_type=doc.get("exam_type", "semester"),
                marks_obtained=float(doc.get("marks_obtained", 0.0)),
                max_marks=float(doc.get("max_marks", 100.0)),
                percentage=float(doc.get("percentage", 0.0)),
                grade=doc.get("grade", "F"),
                academic_year=doc.get("academic_year", ""),
            )
        )

    return MarksReportResponse(
        items=items,
        total=total,
        page=page_num,
        pages=pages,
        limit=page_limit,
    )


def get_academic_summary_report(
    db: Database,
    department: Optional[str] = None,
    semester: Optional[int] = None,
    academic_year: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> AcademicSummaryReportResponse:
    """
    Computes consolidated academic summary metrics with list of students.
    """
    student_report = get_students_report(
        db=db,
        department=department,
        page=page,
        limit=limit,
    )

    # Compute overall summary metrics across the filtered group
    marks_filter: Dict[str, Any] = {}
    if semester is not None:
        marks_filter["semester"] = int(semester)
    if academic_year and academic_year.strip() and academic_year != "All":
        marks_filter["academic_year"] = academic_year.strip()

    if department and department.strip() and department != "All Departments" and department != "All":
        s_ids = [
            s.get("student_id")
            for s in db.students.find({"department": department.strip()})
            if s.get("student_id")
        ]
        marks_filter["student_id"] = {"$in": s_ids}

    marks_docs = list(db.marks.find(marks_filter))
    total_evals = len(marks_docs)
    total_obtained = sum(float(m.get("marks_obtained", 0.0)) for m in marks_docs)
    total_max = sum(float(m.get("max_marks", 0.0)) for m in marks_docs)

    avg_pct = round((total_obtained / total_max) * 100.0, 2) if total_max > 0 else 0.0
    passed_evals = sum(1 for m in marks_docs if float(m.get("percentage", 0.0)) >= 40.0)
    pass_pct = round((passed_evals / total_evals) * 100.0, 2) if total_evals > 0 else 0.0

    grade_dist = {"A+": 0, "A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0}
    for m in marks_docs:
        g = m.get("grade")
        if g in grade_dist:
            grade_dist[g] += 1
        elif g:
            grade_dist[g] = 1

    summary_metrics = AcademicSummaryMetrics(
        department=department if department and department != "All Departments" else "All Departments",
        semester=semester,
        academic_year=academic_year if academic_year and academic_year != "All" else None,
        student_count=student_report.total,
        average_percentage=avg_pct,
        pass_percentage=pass_pct,
        grade_distribution=grade_dist,
    )

    return AcademicSummaryReportResponse(
        summary=summary_metrics,
        students=student_report.items,
        total=student_report.total,
        page=student_report.page,
        pages=student_report.pages,
        limit=student_report.limit,
    )


def export_students_csv(
    db: Database,
    department: Optional[str] = None,
    year: Optional[int] = None,
    section: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> str:
    """
    Generates real-data CSV export stream for Students Report.
    """
    report = get_students_report(
        db=db,
        department=department,
        year=year,
        section=section,
        is_active=is_active,
        page=1,
        limit=5000,
    )

    output = io.StringIO()
    writer = csv.writer(output, dialect="excel")

    # Header Row
    writer.writerow([
        "Student ID",
        "Roll Number",
        "Full Name",
        "Email",
        "Department",
        "Year",
        "Section",
        "Attendance (%)",
        "Academic Average (%)",
        "Risk Level",
        "Status",
    ])

    for s in report.items:
        writer.writerow([
            s.student_id,
            s.roll_number,
            s.full_name,
            s.email,
            s.department,
            f"Year {s.year}",
            s.section,
            f"{s.attendance_percentage}%",
            f"{s.academic_percentage}%",
            s.risk_level,
            "Active" if s.is_active else "Inactive",
        ])

    return output.getvalue()


def export_attendance_csv(
    db: Database,
    department: Optional[str] = None,
    year: Optional[int] = None,
    section: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    student_id: Optional[str] = None,
    status: Optional[str] = None,
) -> str:
    """
    Generates real-data CSV export stream for Attendance Report.
    """
    report = get_attendance_report(
        db=db,
        department=department,
        year=year,
        section=section,
        date_from=date_from,
        date_to=date_to,
        student_id=student_id,
        status=status,
        page=1,
        limit=5000,
    )

    output = io.StringIO()
    writer = csv.writer(output, dialect="excel")

    writer.writerow([
        "Attendance ID",
        "Student ID",
        "Student Name",
        "Roll Number",
        "Department",
        "Date",
        "Status",
        "Remarks",
        "Marked By",
    ])

    for a in report.items:
        writer.writerow([
            a.attendance_id,
            a.student_id,
            a.student_name,
            a.roll_number,
            a.department,
            a.date,
            a.status.capitalize(),
            a.remarks or "",
            a.marked_by,
        ])

    return output.getvalue()


def export_marks_csv(
    db: Database,
    department: Optional[str] = None,
    semester: Optional[int] = None,
    subject_code: Optional[str] = None,
    exam_type: Optional[str] = None,
    academic_year: Optional[str] = None,
    student_id: Optional[str] = None,
) -> str:
    """
    Generates real-data CSV export stream for Marks Report.
    """
    report = get_marks_report(
        db=db,
        department=department,
        semester=semester,
        subject_code=subject_code,
        exam_type=exam_type,
        academic_year=academic_year,
        student_id=student_id,
        page=1,
        limit=5000,
    )

    output = io.StringIO()
    writer = csv.writer(output, dialect="excel")

    writer.writerow([
        "Marks ID",
        "Student ID",
        "Student Name",
        "Roll Number",
        "Department",
        "Subject Code",
        "Subject Name",
        "Semester",
        "Exam Type",
        "Marks Obtained",
        "Max Marks",
        "Percentage (%)",
        "Grade",
        "Academic Year",
    ])

    for m in report.items:
        writer.writerow([
            m.marks_id,
            m.student_id,
            m.student_name,
            m.roll_number,
            m.department,
            m.subject_code,
            m.subject_name,
            f"Sem {m.semester}",
            m.exam_type,
            m.marks_obtained,
            m.max_marks,
            f"{m.percentage}%",
            m.grade,
            m.academic_year,
        ])

    return output.getvalue()


def generate_student_pdf_bytes(
    db: Database,
    student_id: str,
) -> bytes:
    """
    Generates a standard ISO 32000-1 valid PDF document for a student academic report.
    Built in pure Python with zero external binary dependencies.
    """
    student = get_student_by_identifier(db, student_id.strip())
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with identifier '{student_id}' was not found.",
        )

    canonical_id = student.student_id
    att_sum = calculate_attendance_summary(db, canonical_id)
    mrk_sum = calculate_student_marks_summary(db, canonical_id)
    risk = calculate_student_risk(db, canonical_id)
    marks_records = list(db.marks.find({"student_id": canonical_id}).sort("semester", 1))

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Construct clean PDF text streams
    lines = [
        "EduManage - Official Academic Performance Report",
        "====================================================",
        f"Generated: {now_str}",
        "",
        f"Student Name:   {student.full_name}",
        f"Student ID:     {canonical_id}",
        f"Roll Number:    {student.roll_number}",
        f"Email:          {student.email}",
        f"Department:     {student.department}",
        f"Academic Year:  Year {student.year} (Section {student.section})",
        f"Status:         {'Active' if student.is_active else 'Inactive'}",
        "",
        "--- ACADEMIC & ATTENDANCE SUMMARY ---",
        f"Overall Attendance:   {att_sum.attendance_percentage}% ({att_sum.present_days}/{att_sum.total_days} sessions attended)",
        f"Overall Marks Score:  {mrk_sum.overall_percentage}% ({mrk_sum.total_marks_obtained}/{mrk_sum.total_max_marks} marks)",
        f"Passed Subjects:      {mrk_sum.passed_subjects}/{mrk_sum.total_subjects}",
        f"AI Academic Risk:     {risk.risk_level.value} (Risk Score: {risk.risk_score}/100)",
        "",
        "--- ASSESSMENT EVALUATIONS ---",
        f"{'Subject':<10} {'Subject Title':<28} {'Sem':<5} {'Exam Type':<12} {'Score':<10} {'Grade':<6}",
        "-" * 75,
    ]

    for m in marks_records:
        scode = str(m.get("subject_code", ""))[:9]
        sname = str(m.get("subject_name", ""))[:26]
        sem = str(m.get("semester", ""))
        etype = str(m.get("exam_type", ""))[:11]
        score = f"{m.get('marks_obtained', 0)}/{m.get('max_marks', 100)}"
        grd = str(m.get("grade", ""))
        lines.append(f"{scode:<10} {sname:<28} {sem:<5} {etype:<12} {score:<10} {grd:<6}")

    if not marks_records:
        lines.append("No marks evaluations recorded for this student yet.")

    lines.extend([
        "",
        "--- KEY DIAGNOSTIC INSIGHTS & RECOMMENDATIONS ---",
    ])
    for factor in risk.key_factors:
        lines.append(f"  * {factor}")
    for rec in risk.recommendations:
        lines.append(f"  > Recommendation: {rec}")

    lines.extend([
        "",
        "====================================================",
        "EduManage Institutional Academic System - Confidential",
    ])

    # Format text into valid PDF content stream
    text_commands = ["BT", "/F1 10 Tf", "14 TL", "40 770 Td"]
    for i, line in enumerate(lines):
        # Escape parenthesis and backslashes for PDF string literal
        escaped_line = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        if i == 0:
            text_commands.append(f"({escaped_line}) Tj")
        else:
            text_commands.append(f"T* ({escaped_line}) Tj")
    text_commands.append("ET")

    stream_data = "\n".join(text_commands).encode("latin1", "replace")
    stream_len = len(stream_data)

    # Build standard PDF object structure
    pdf_parts = []
    pdf_parts.append(b"%PDF-1.4\n")
    
    offsets = []
    current_pos = len(pdf_parts[0])

    # Object 1: Catalog
    offsets.append(current_pos)
    obj1 = b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    pdf_parts.append(obj1)
    current_pos += len(obj1)

    # Object 2: Pages
    offsets.append(current_pos)
    obj2 = b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
    pdf_parts.append(obj2)
    current_pos += len(obj2)

    # Object 3: Page
    offsets.append(current_pos)
    obj3 = b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
    pdf_parts.append(obj3)
    current_pos += len(obj3)

    # Object 4: Contents Stream
    offsets.append(current_pos)
    obj4_header = f"4 0 obj\n<< /Length {stream_len} >>\nstream\n".encode("ascii")
    obj4_footer = b"\nendstream\nendobj\n"
    pdf_parts.append(obj4_header)
    pdf_parts.append(stream_data)
    pdf_parts.append(obj4_footer)
    current_pos += len(obj4_header) + len(stream_data) + len(obj4_footer)

    # Object 5: Font
    offsets.append(current_pos)
    obj5 = b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>\nendobj\n"
    pdf_parts.append(obj5)
    current_pos += len(obj5)

    # Cross Reference Table (xref)
    xref_pos = current_pos
    xref_header = f"xref\n0 6\n0000000000 65535 f \n".encode("ascii")
    pdf_parts.append(xref_header)
    for offset in offsets:
        pdf_parts.append(f"{offset:010d} 00000 n \n".encode("ascii"))

    trailer = f"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("ascii")
    pdf_parts.append(trailer)

    return b"".join(pdf_parts)
