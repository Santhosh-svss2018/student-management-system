"""
Reports & Data Export Models
Defines Pydantic schemas for filterable institutional reports and export outputs.
"""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class StudentReportItem(BaseModel):
    student_id: str
    roll_number: str
    full_name: str
    email: str
    department: str
    year: int
    section: str
    attendance_percentage: float
    academic_percentage: float
    risk_level: str
    is_active: bool


class StudentReportResponse(BaseModel):
    items: List[StudentReportItem]
    total: int
    page: int
    pages: int
    limit: int


class AttendanceReportItem(BaseModel):
    attendance_id: str
    student_id: str
    student_name: str
    roll_number: str
    department: str
    date: str
    status: str
    remarks: Optional[str] = None
    marked_by: str


class AttendanceReportResponse(BaseModel):
    items: List[AttendanceReportItem]
    total: int
    page: int
    pages: int
    limit: int


class MarksReportItem(BaseModel):
    marks_id: str
    student_id: str
    student_name: str
    roll_number: str
    department: str
    subject_code: str
    subject_name: str
    semester: int
    exam_type: str
    marks_obtained: float
    max_marks: float
    percentage: float
    grade: str
    academic_year: str


class MarksReportResponse(BaseModel):
    items: List[MarksReportItem]
    total: int
    page: int
    pages: int
    limit: int


class AcademicSummaryMetrics(BaseModel):
    department: Optional[str] = None
    semester: Optional[int] = None
    academic_year: Optional[str] = None
    student_count: int
    average_percentage: float
    pass_percentage: float
    grade_distribution: Dict[str, int]


class AcademicSummaryReportResponse(BaseModel):
    summary: AcademicSummaryMetrics
    students: List[StudentReportItem]
    total: int
    page: int
    pages: int
    limit: int
