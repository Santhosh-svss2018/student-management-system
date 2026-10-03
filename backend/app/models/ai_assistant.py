"""
AI Assistant Data Models & Schemas
Defines request and response schemas, chat message structures, and validation rules for the EduAI Assistant.
"""

from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class ChatMessage(BaseModel):
    """Represents a single message in an academic assistant conversation."""
    role: str = Field(..., description="Message author role ('user', 'assistant', or 'system')")
    content: str = Field(..., description="Message text content")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Message creation timestamp",
    )


class AssistantRequest(BaseModel):
    """Incoming user query payload to the EduAI assistant endpoint."""
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User question or prompt for the academic assistant",
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Optional client conversation identifier",
    )

    @field_validator("message")
    @classmethod
    def validate_non_empty_message(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Message query cannot be empty or whitespace only.")
        return trimmed


class AssistantResponse(BaseModel):
    """Structured response returned by the EduAI assistant endpoint."""
    response: str = Field(..., description="Assistant response text in markdown format")
    role: str = Field(..., description="Authenticated user role that initiated the query")
    context_used: List[str] = Field(
        default_factory=list,
        description="List of domain context modules retrieved (e.g., 'attendance', 'marks', 'risk_analysis')",
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Contextual follow-up suggestions tailored to user role and query",
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Active conversation session identifier",
    )
