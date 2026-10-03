"""
AI Assistant Endpoint Module
Handles contextual, role-based chat requests for the EduAI Academic Assistant.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database

from app.api.deps import get_db, require_authenticated_user
from app.models.ai_assistant import AssistantRequest, AssistantResponse
from app.models.user import UserInDB
from app.services.ai_assistant_service import process_assistant_chat

logger = logging.getLogger("edumanage.api.ai_assistant")

router = APIRouter()


@router.post(
    "/chat",
    response_model=AssistantResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat with EduAI Academic Assistant",
    description=(
        "Processes an academic inquiry contextualized by the authenticated user's role "
        "and authorized MongoDB records (Student, Attendance, Marks, and Risk Analysis)."
    ),
)
def chat_with_assistant(
    request: AssistantRequest,
    db: Database = Depends(get_db),
    current_user: UserInDB = Depends(require_authenticated_user),
) -> AssistantResponse:
    """
    Role-aware chat endpoint for Students, Teachers, and Administrators.
    Validates authentication and RBAC boundaries before delivering live application data.
    """
    try:
        response = process_assistant_chat(
            db=db,
            current_user=current_user,
            request=request,
        )
        return response
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Unhandled error in EduAI Assistant chat: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request with the academic assistant.",
        ) from exc
