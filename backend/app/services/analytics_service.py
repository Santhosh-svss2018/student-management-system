"""
Analytics Service Module
Provides MongoDB-backed analytics and institutional metrics for Admin, Teacher, and Student dashboards.
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
from pymongo.database import Database

from app.models.ai_insights import RiskLevel
from app.models.analytics import (
    AdminAcademicAnalytics,
    AdminAttendanceAnalytics,
    AdminDepartmentsAnalytics,
    AdminOverviewAnalytics,
    AttendanceDefaulterItem,
    AttendanceDistribution,
    AttendanceTrendItem,
    DepartmentAnalyticsItem,
    DepartmentAttendanceItem,
    DepartmentDistributionItem,
    SectionDistributionItem,
    SemesterPerformanceItem,
    StudentAnalyticsResponse,
    SubjectPerformanceItem,
    TeacherOverviewAnalytics,
    YearDistributionItem,
)
from app.services.ai_insights_service import calculate_student_risk, get_institutional_risk_summary
from app.services.attendance_service import calculate_attendance_summary
from app.services.marks_service import calculate_student_marks_summary
from app.services.student_service import get_student_by_email, get_student_by_identifier

logger = logging.getLogger("edumanage.services.analytics")


def get_admin_overview_analytics(db: Database) -> AdminOverviewAnalytics:
    """
    Computes real-time institutional overview metrics from MongoDB.
    """
    total_students = db.students.count_documents({})
    active_students = db.students.count_documents({"is_active": True})
    inactive_students = db.students.count_documents({"is_active": False})
    total_teachers = db.users.count_documents({"role": "teacher", "is_active": True})
    total_attendance_records = db.attendance.count_documents({})
    total_marks_records = db.marks.count_documents({})

    # 1. Attendance Distribution & Overall Percentage
    present_count = db.attendance.count_documents({"status": "present"})
    absent_count = db.attendance.count_documents({"status": "absent"})
    late_count = db.attendance.count_documents({"status": "late"})
    excused_count = db.attendance.count_documents({"status": "excused"})

    overall_att_pct = (
        round((present_count / total_attendance_records) * 100.0, 2)
        if total_attendance_records > 0
        else 0.0
    )

    attendance_dist = AttendanceDistribution(
        present=present_count,
        absent=absent_count,
        late=late_count,
        excused=excused_count,
        total=total_attendance_records,
        overall_percentage=overall_att_pct,
    )

    # 2. Academic Grade Distribution & Overall Percentage
    grade_distribution = {"A+": 0, "A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0}
    marks_cursor = db.marks.find({})
    total_marks_obtained = 0.0
    total_max_marks = 0.0

    for m in marks_cursor:
        g = m.get("grade")
        if g in grade_distribution:
            grade_distribution[g] += 1
        elif g:
            grade_distribution[g] = 1

        total_marks_obtained += float(m.get("marks_obtained", 0.0))
        total_max_marks += float(m.get("max_marks", 0.0))

    overall_academic_pct = (
        round((total_marks_obtained / total_max_marks) * 100.0, 2)
        if total_max_marks > 0
        else 0.0
    )

    # 3. AI Risk Summary
    risk_summary = get_institutional_risk_summary(db=db, limit=1000)
    students_at_risk = (
        risk_summary.medium_count + risk_summary.high_count + risk_summary.critical_count
    )
    high_risk_students = risk_summary.high_count
    critical_risk_students = risk_summary.critical_count

    # 4. Demographic Distributions (Department, Year, Section)
    dept_counts: Dict[str, int] = {}
    year_counts: Dict[int, int] = {}
    section_counts: Dict[str, int] = {}

    all_students = list(db.students.find({"is_active": True}))
    for s in all_students:
        d = s.get("department", "Unassigned")
        dept_counts[d] = dept_counts.get(d, 0) + 1

        y = s.get("year", 1)
        year_counts[y] = year_counts.get(y, 0) + 1

        sec = s.get("section", "A")
        section_counts[sec] = section_counts.get(sec, 0) + 1

    active_count = len(all_students)
    department_distribution = [
        DepartmentDistributionItem(
            department=dept,
            count=count,
            percentage=round((count / active_count) * 100.0, 2) if active_count > 0 else 0.0,
        )
        for dept, count in sorted(dept_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    year_distribution = [
        YearDistributionItem(
            year=year,
            count=count,
            percentage=round((count / active_count) * 100.0, 2) if active_count > 0 else 0.0,
        )
        for year, count in sorted(year_counts.items(), key=lambda x: x[0])
    ]

    section_distribution = [
        SectionDistributionItem(
            section=sec,
            count=count,
            percentage=round((count / active_count) * 100.0, 2) if active_count > 0 else 0.0,
        )
        for sec, count in sorted(section_counts.items(), key=lambda x: x[0])
    ]

    return AdminOverviewAnalytics(
        total_students=total_students,
        active_students=active_students,
        inactive_students=inactive_students,
        total_teachers=total_teachers,
        total_attendance_records=total_attendance_records,
        overall_attendance_percentage=overall_att_pct,
        total_marks_records=total_marks_records,
        overall_academic_percentage=overall_academic_pct,
        students_at_risk=students_at_risk,
        high_risk_students=high_risk_students,
        critical_risk_students=critical_risk_students,
        department_distribution=department_distribution,
        year_distribution=year_distribution,
        section_distribution=section_distribution,
        attendance_distribution=attendance_dist,
        grade_distribution=grade_distribution,
        generated_at=datetime.now(timezone.utc),
    )


def get_admin_departments_analytics(db: Database) -> AdminDepartmentsAnalytics:
    """
    Computes department-level statistics dynamically from MongoDB data.
    """
    departments = db.students.distinct("department")
    dept_items: List[DepartmentAnalyticsItem] = []

    for dept in departments:
        if not dept or not str(dept).strip():
            continue
        dept_str = str(dept).strip()
        dept_students = list(db.students.find({"department": dept_str, "is_active": True}))
        student_count = len(dept_students)

        if student_count == 0:
            continue

        student_ids = [s.get("student_id") for s in dept_students if s.get("student_id")]

        # Attendance percentage for this department
        att_records = list(db.attendance.find({"student_id": {"$in": student_ids}}))
        total_att = len(att_records)
        present_att = sum(1 for r in att_records if r.get("status") == "present")
        att_pct = (
            round((present_att / total_att) * 100.0, 2) if total_att > 0 else 0.0
        )

        # Academic percentage for this department
        marks_records = list(db.marks.find({"student_id": {"$in": student_ids}}))
        total_obtained = sum(float(m.get("marks_obtained", 0.0)) for m in marks_records)
        total_max = sum(float(m.get("max_marks", 0.0)) for m in marks_records)
        acad_pct = (
            round((total_obtained / total_max) * 100.0, 2) if total_max > 0 else 0.0
        )

        # At-risk count
        at_risk = 0
        for sid in student_ids:
            try:
                risk = calculate_student_risk(db, sid)
                if risk.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]:
                    at_risk += 1
            except Exception:
                pass

        dept_items.append(
            DepartmentAnalyticsItem(
                department=dept_str,
                student_count=student_count,
                attendance_percentage=att_pct,
                academic_percentage=acad_pct,
                at_risk_count=at_risk,
            )
        )

    dept_items.sort(key=lambda x: x.student_count, reverse=True)

    return AdminDepartmentsAnalytics(
        departments=dept_items,
        total_departments=len(dept_items),
        generated_at=datetime.now(timezone.utc),
    )


def get_admin_academic_analytics(db: Database) -> AdminAcademicAnalytics:
    """
    Calculates detailed institutional academic performance analytics.
    """
    marks_records = list(db.marks.find({}))
    total_evaluations = len(marks_records)

    grade_distribution = {"A+": 0, "A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0}
    subject_map: Dict[str, Dict[str, Any]] = {}
    semester_map: Dict[int, Dict[str, Any]] = {}

    total_marks_obtained = 0.0
    total_max_marks = 0.0
    passed_count = 0

    for m in marks_records:
        g = m.get("grade")
        if g in grade_distribution:
            grade_distribution[g] += 1
        elif g:
            grade_distribution[g] = 1

        obt = float(m.get("marks_obtained", 0.0))
        mx = float(m.get("max_marks", 0.0))
        pct = float(m.get("percentage", 0.0))

        total_marks_obtained += obt
        total_max_marks += mx
        if pct >= 40.0:
            passed_count += 1

        # Subject aggregation
        scode = m.get("subject_code", "UNKNOWN")
        sname = m.get("subject_name", scode)
        if scode not in subject_map:
            subject_map[scode] = {
                "subject_code": scode,
                "subject_name": sname,
                "total_pct": 0.0,
                "count": 0,
                "passed": 0,
            }
        subject_map[scode]["total_pct"] += pct
        subject_map[scode]["count"] += 1
        if pct >= 40.0:
            subject_map[scode]["passed"] += 1

        # Semester aggregation
        sem = int(m.get("semester", 1))
        if sem not in semester_map:
            semester_map[sem] = {
                "semester": sem,
                "total_pct": 0.0,
                "count": 0,
            }
        semester_map[sem]["total_pct"] += pct
        semester_map[sem]["count"] += 1

    overall_avg_pct = (
        round((total_marks_obtained / total_max_marks) * 100.0, 2)
        if total_max_marks > 0
        else 0.0
    )
    pass_pct = (
        round((passed_count / total_evaluations) * 100.0, 2)
        if total_evaluations > 0
        else 0.0
    )
    fail_pct = round(100.0 - pass_pct, 2) if total_evaluations > 0 else 0.0

    subject_performance: List[SubjectPerformanceItem] = []
    for scode, sdata in subject_map.items():
        cnt = sdata["count"]
        avg_p = round(sdata["total_pct"] / cnt, 2) if cnt > 0 else 0.0
        pass_p = round((sdata["passed"] / cnt) * 100.0, 2) if cnt > 0 else 0.0
        subject_performance.append(
            SubjectPerformanceItem(
                subject_code=scode,
                subject_name=sdata["subject_name"],
                average_percentage=avg_p,
                student_count=cnt,
                pass_percentage=pass_p,
            )
        )
    subject_performance.sort(key=lambda x: x.average_percentage, reverse=True)

    highest_performing = subject_performance[0].subject_code if subject_performance else None
    lowest_performing = subject_performance[-1].subject_code if subject_performance else None

    semester_performance: List[SemesterPerformanceItem] = []
    for sem, semdata in sorted(semester_map.items(), key=lambda x: x[0]):
        cnt = semdata["count"]
        avg_p = round(semdata["total_pct"] / cnt, 2) if cnt > 0 else 0.0
        semester_performance.append(
            SemesterPerformanceItem(
                semester=sem,
                average_percentage=avg_p,
                student_count=cnt,
            )
        )

    return AdminAcademicAnalytics(
        grade_distribution=grade_distribution,
        subject_performance=subject_performance,
        semester_performance=semester_performance,
        pass_percentage=pass_pct,
        fail_percentage=fail_pct,
        average_percentage=overall_avg_pct,
        highest_performing_subject=highest_performing,
        lowest_performing_subject=lowest_performing,
        total_marks_evaluated=total_evaluations,
        generated_at=datetime.now(timezone.utc),
    )


def get_admin_attendance_analytics(db: Database) -> AdminAttendanceAnalytics:
    """
    Calculates detailed institutional attendance metrics, trends, and defaulters.
    """
    attendance_records = list(db.attendance.find({}))
    total_records = len(attendance_records)

    present_count = sum(1 for r in attendance_records if r.get("status") == "present")
    absent_count = sum(1 for r in attendance_records if r.get("status") == "absent")
    late_count = sum(1 for r in attendance_records if r.get("status") == "late")
    excused_count = sum(1 for r in attendance_records if r.get("status") == "excused")

    overall_att = (
        round((present_count / total_records) * 100.0, 2) if total_records > 0 else 0.0
    )
    present_pct = (
        round((present_count / total_records) * 100.0, 2) if total_records > 0 else 0.0
    )
    absent_pct = (
        round((absent_count / total_records) * 100.0, 2) if total_records > 0 else 0.0
    )
    late_pct = (
        round((late_count / total_records) * 100.0, 2) if total_records > 0 else 0.0
    )
    excused_pct = (
        round((excused_count / total_records) * 100.0, 2) if total_records > 0 else 0.0
    )

    # 1. Attendance trend by date
    date_map: Dict[str, Dict[str, int]] = {}
    for r in attendance_records:
        dt = r.get("date", "Unknown")
        st = r.get("status", "present")
        if dt not in date_map:
            date_map[dt] = {"present": 0, "absent": 0, "late": 0, "excused": 0, "total": 0}
        date_map[dt]["total"] += 1
        if st in date_map[dt]:
            date_map[dt][st] += 1

    attendance_trend: List[AttendanceTrendItem] = []
    for dt, counts in sorted(date_map.items(), key=lambda x: x[0]):
        tot = counts["total"]
        pct = round((counts["present"] / tot) * 100.0, 2) if tot > 0 else 0.0
        attendance_trend.append(
            AttendanceTrendItem(
                date=dt,
                present_count=counts["present"],
                absent_count=counts["absent"],
                late_count=counts["late"],
                excused_count=counts["excused"],
                total=tot,
                percentage=pct,
            )
        )

    # 2. Department attendance
    active_students = list(db.students.find({"is_active": True}))
    dept_student_map: Dict[str, List[str]] = {}
    for s in active_students:
        d = s.get("department", "Unassigned")
        dept_student_map.setdefault(d, []).append(s.get("student_id"))

    department_attendance: List[DepartmentAttendanceItem] = []
    for dept, sids in dept_student_map.items():
        dept_att = list(db.attendance.find({"student_id": {"$in": sids}}))
        tot = len(dept_att)
        prs = sum(1 for r in dept_att if r.get("status") == "present")
        pct = round((prs / tot) * 100.0, 2) if tot > 0 else 0.0
        department_attendance.append(
            DepartmentAttendanceItem(
                department=dept,
                attendance_percentage=pct,
                total_sessions=tot,
            )
        )

    # 3. Attendance Defaulters (Active students with < 75% attendance and total_days > 0)
    defaulters: List[AttendanceDefaulterItem] = []
    for s in active_students:
        sid = s.get("student_id")
        if not sid:
            continue
        summary = calculate_attendance_summary(db, sid)
        if summary.total_days > 0 and summary.attendance_percentage < 75.0:
            defaulters.append(
                AttendanceDefaulterItem(
                    student_id=sid,
                    student_name=s.get("full_name", "Student"),
                    department=s.get("department", "Unassigned"),
                    attendance_percentage=summary.attendance_percentage,
                    total_days=summary.total_days,
                    present_days=summary.present_days,
                )
            )

    defaulters.sort(key=lambda x: x.attendance_percentage)

    return AdminAttendanceAnalytics(
        overall_attendance=overall_att,
        present_percentage=present_pct,
        absent_percentage=absent_pct,
        late_percentage=late_pct,
        excused_percentage=excused_pct,
        attendance_trend=attendance_trend,
        department_attendance=department_attendance,
        attendance_defaulters=defaulters,
        total_records=total_records,
        generated_at=datetime.now(timezone.utc),
    )


def get_teacher_overview_analytics(
    db: Database,
    current_user_email: str,
    department: Optional[str] = None,
) -> TeacherOverviewAnalytics:
    """
    Computes authorized teacher analytics for class overview, attendance, and student performance.
    """
    # Teacher user
    user_doc = db.users.find_one({"email": current_user_email.strip().lower()})
    user_dept = user_doc.get("department") if user_doc else None

    target_dept = department.strip() if department and department.strip() else user_dept
    student_query: Dict[str, Any] = {"is_active": True}
    if target_dept:
        student_query["department"] = target_dept

    students = list(db.students.find(student_query))
    student_count = len(students)
    student_ids = [s.get("student_id") for s in students if s.get("student_id")]

    # Attendance Overview
    att_records = list(db.attendance.find({"student_id": {"$in": student_ids}}))
    total_sessions = len(att_records)
    present_count = sum(1 for r in att_records if r.get("status") == "present")
    absent_count = sum(1 for r in att_records if r.get("status") == "absent")
    att_pct = (
        round((present_count / total_sessions) * 100.0, 2) if total_sessions > 0 else 0.0
    )

    attendance_overview = {
        "total_sessions": total_sessions,
        "present_count": present_count,
        "absent_count": absent_count,
        "attendance_percentage": att_pct,
    }

    # Defaulters in teacher's scope
    defaulters: List[AttendanceDefaulterItem] = []
    attention_list: List[Dict[str, Any]] = []

    for s in students:
        sid = s.get("student_id")
        if not sid:
            continue
        att_sum = calculate_attendance_summary(db, sid)
        if att_sum.total_days > 0 and att_sum.attendance_percentage < 75.0:
            defaulters.append(
                AttendanceDefaulterItem(
                    student_id=sid,
                    student_name=s.get("full_name", "Student"),
                    department=s.get("department", "Unassigned"),
                    attendance_percentage=att_sum.attendance_percentage,
                    total_days=att_sum.total_days,
                    present_days=att_sum.present_days,
                )
            )

        try:
            risk = calculate_student_risk(db, sid)
            if risk.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                attention_list.append({
                    "student_id": sid,
                    "student_name": s.get("full_name", "Student"),
                    "department": s.get("department", "Unassigned"),
                    "risk_level": risk.risk_level.value,
                    "risk_score": risk.risk_score,
                    "attendance_percentage": risk.attendance_percentage,
                    "academic_percentage": risk.academic_percentage,
                    "reason": (
                        risk.key_factors[0]
                        if risk.key_factors
                        else "Requires faculty intervention"
                    ),
                })
        except Exception:
            pass

    # Academic Performance
    marks_records = list(db.marks.find({"student_id": {"$in": student_ids}}))
    total_evals = len(marks_records)
    total_obtained = sum(float(m.get("marks_obtained", 0.0)) for m in marks_records)
    total_max = sum(float(m.get("max_marks", 0.0)) for m in marks_records)
    overall_acad_pct = (
        round((total_obtained / total_max) * 100.0, 2) if total_max > 0 else 0.0
    )
    passed_evals = sum(1 for m in marks_records if float(m.get("percentage", 0.0)) >= 40.0)
    pass_pct = (
        round((passed_evals / total_evals) * 100.0, 2) if total_evals > 0 else 0.0
    )

    academic_performance = {
        "overall_percentage": overall_acad_pct,
        "pass_percentage": pass_pct,
        "total_evaluations": total_evals,
    }

    # Grade Distribution
    grade_distribution = {"A+": 0, "A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0}
    for m in marks_records:
        g = m.get("grade")
        if g in grade_distribution:
            grade_distribution[g] += 1
        elif g:
            grade_distribution[g] = 1

    return TeacherOverviewAnalytics(
        student_count=student_count,
        attendance_overview=attendance_overview,
        attendance_defaulters=defaulters,
        academic_performance=academic_performance,
        grade_distribution=grade_distribution,
        students_requiring_attention=attention_list,
        generated_at=datetime.now(timezone.utc),
    )


def get_student_self_analytics(
    db: Database,
    current_user_email: str,
) -> StudentAnalyticsResponse:
    """
    Fetches real-time personal analytics for the authenticated student.
    Strictly isolates data to only the verified student.
    """
    student = get_student_by_email(db, current_user_email.strip().lower())
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found for this account.",
        )

    canonical_id = student.student_id

    # 1. Attendance Metrics & Trend
    att_summary = calculate_attendance_summary(db, canonical_id)
    att_records = list(
        db.attendance.find({"student_id": canonical_id}).sort("date", -1).limit(10)
    )
    attendance_trend = [
        AttendanceTrendItem(
            date=r.get("date", "Unknown"),
            present_count=1 if r.get("status") == "present" else 0,
            absent_count=1 if r.get("status") == "absent" else 0,
            late_count=1 if r.get("status") == "late" else 0,
            excused_count=1 if r.get("status") == "excused" else 0,
            total=1,
            percentage=100.0 if r.get("status") == "present" else 0.0,
        )
        for r in att_records
    ]

    # 2. Marks Performance & Grade Distribution
    marks_summary = calculate_student_marks_summary(db, canonical_id)

    # 3. AI Risk Analysis
    risk_analysis = calculate_student_risk(db, canonical_id)

    return StudentAnalyticsResponse(
        student_id=canonical_id,
        student_name=student.full_name,
        department=student.department,
        year=student.year,
        section=student.section,
        roll_number=student.roll_number,
        attendance_percentage=att_summary.attendance_percentage,
        attendance_summary=att_summary,
        attendance_trend=attendance_trend,
        marks_summary=marks_summary,
        grade_distribution=marks_summary.grade_distribution,
        academic_percentage=marks_summary.overall_percentage,
        passed_subjects=marks_summary.passed_subjects,
        failed_subjects=marks_summary.failed_subjects,
        risk_level=risk_analysis.risk_level.value,
        risk_score=risk_analysis.risk_score,
        risk_factors=risk_analysis.key_factors,
        recommendations=risk_analysis.recommendations,
        generated_at=datetime.now(timezone.utc),
    )
