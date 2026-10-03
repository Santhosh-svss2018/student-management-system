"""
Analytics & Institutional Metrics Models
Defines Pydantic schemas for Admin, Teacher, and Student analytics dashboards.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from app.models.attendance import AttendanceSummaryResponse
from app.models.marks import MarksSummaryResponse


class DepartmentDistributionItem(BaseModel):
    department: str
    count: int
    percentage: float


class YearDistributionItem(BaseModel):
    year: int
    count: int
    percentage: float


class SectionDistributionItem(BaseModel):
    section: str
    count: int
    percentage: float


class AttendanceDistribution(BaseModel):
    present: int = 0
    absent: int = 0
    late: int = 0
    excused: int = 0
    total: int = 0
    overall_percentage: float = 0.0


class AdminOverviewAnalytics(BaseModel):
    total_students: int
    active_students: int
    inactive_students: int
    total_teachers: int
    total_attendance_records: int
    overall_attendance_percentage: float
    total_marks_records: int
    overall_academic_percentage: float
    students_at_risk: int
    high_risk_students: int
    critical_risk_students: int
    department_distribution: List[DepartmentDistributionItem]
    year_distribution: List[YearDistributionItem]
    section_distribution: List[SectionDistributionItem]
    attendance_distribution: AttendanceDistribution
    grade_distribution: Dict[str, int]
    generated_at: datetime


class DepartmentAnalyticsItem(BaseModel):
    department: str
    student_count: int
    attendance_percentage: float
    academic_percentage: float
    at_risk_count: int


class AdminDepartmentsAnalytics(BaseModel):
    departments: List[DepartmentAnalyticsItem]
    total_departments: int
    generated_at: datetime


class SubjectPerformanceItem(BaseModel):
    subject_code: str
    subject_name: str
    average_percentage: float
    student_count: int
    pass_percentage: float


class SemesterPerformanceItem(BaseModel):
    semester: int
    average_percentage: float
    student_count: int


class AdminAcademicAnalytics(BaseModel):
    grade_distribution: Dict[str, int]
    subject_performance: List[SubjectPerformanceItem]
    semester_performance: List[SemesterPerformanceItem]
    pass_percentage: float
    fail_percentage: float
    average_percentage: float
    highest_performing_subject: Optional[str] = None
    lowest_performing_subject: Optional[str] = None
    total_marks_evaluated: int
    generated_at: datetime


class AttendanceTrendItem(BaseModel):
    date: str
    present_count: int
    absent_count: int
    late_count: int
    excused_count: int
    total: int
    percentage: float


class DepartmentAttendanceItem(BaseModel):
    department: str
    attendance_percentage: float
    total_sessions: int


class AttendanceDefaulterItem(BaseModel):
    student_id: str
    student_name: str
    department: str
    attendance_percentage: float
    total_days: int
    present_days: int


class AdminAttendanceAnalytics(BaseModel):
    overall_attendance: float
    present_percentage: float
    absent_percentage: float
    late_percentage: float
    excused_percentage: float
    attendance_trend: List[AttendanceTrendItem]
    department_attendance: List[DepartmentAttendanceItem]
    attendance_defaulters: List[AttendanceDefaulterItem]
    total_records: int
    generated_at: datetime


class TeacherOverviewAnalytics(BaseModel):
    student_count: int
    attendance_overview: Dict[str, Any]
    attendance_defaulters: List[AttendanceDefaulterItem]
    academic_performance: Dict[str, Any]
    grade_distribution: Dict[str, int]
    students_requiring_attention: List[Dict[str, Any]]
    generated_at: datetime


class StudentAnalyticsResponse(BaseModel):
    student_id: str
    student_name: str
    department: str
    year: int
    section: str
    roll_number: str
    attendance_percentage: float
    attendance_summary: AttendanceSummaryResponse
    attendance_trend: List[AttendanceTrendItem]
    marks_summary: MarksSummaryResponse
    grade_distribution: Dict[str, int]
    academic_percentage: float
    passed_subjects: int
    failed_subjects: int
    risk_level: str
    risk_score: float
    risk_factors: List[str]
    recommendations: List[str]
    generated_at: datetime
