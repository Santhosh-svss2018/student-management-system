"""
API v1 Router Aggregator
Includes all sub-routers for version 1 of the EduManage API.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    ai_assistant,
    ai_insights,
    analytics,
    attendance,
    auth,
    marks,
    rbac_demo,
    reports,
    students,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(users.router, prefix="/admin/users", tags=["Admin Users"])
api_router.include_router(students.router, prefix="/students", tags=["Students"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["Attendance"])
api_router.include_router(marks.router, prefix="/marks", tags=["Marks"])
api_router.include_router(ai_insights.router, prefix="/ai-insights", tags=["AI Insights"])
api_router.include_router(ai_assistant.router, prefix="/ai-assistant", tags=["AI Assistant"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(rbac_demo.router, prefix="/test", tags=["RBAC Test"])



