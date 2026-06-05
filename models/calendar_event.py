"""
Calendar Event Data Models

Pydantic models for calendar events and time slots
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class CalendarEvent(BaseModel):
    """Calendar event model"""

    id: str = Field(..., description="Event unique identifier")
    title: str = Field(..., description="Event title")
    description: str = Field(default="", description="Event description")
    location: str = Field(default="", description="Event location")
    start_time: datetime = Field(..., description="Event start time")
    end_time: datetime = Field(..., description="Event end time")
    attendees: List[str] = Field(default_factory=list, description="Attendee email list")
    organizer: str = Field(default="", description="Organizer email")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "evt_001",
                "title": "团队周会",
                "description": "每周团队同步会议",
                "location": "会议室A",
                "start_time": "2026-06-10T14:00:00",
                "end_time": "2026-06-10T15:00:00",
                "attendees": ["alice@example.com", "bob@example.com"],
                "organizer": "manager@example.com"
            }
        }


class TimeSlot(BaseModel):
    """Time slot model for availability"""

    start: datetime = Field(..., description="Slot start time")
    end: datetime = Field(..., description="Slot end time")
    time_str: str = Field(default="", description="Time string like '14:00'")
    is_available: bool = Field(default=True, description="Whether slot is available")

    class Config:
        json_schema_extra = {
            "example": {
                "start": "2026-06-13T14:00:00",
                "end": "2026-06-13T15:00:00",
                "time_str": "14:00",
                "is_available": True
            }
        }


class ConflictResult(BaseModel):
    """Conflict detection result"""

    has_conflict: bool = Field(..., description="Whether there is a conflict")
    conflicting_events: List[CalendarEvent] = Field(
        default_factory=list,
        description="List of conflicting events"
    )
    suggested_slots: List[TimeSlot] = Field(
        default_factory=list,
        description="Suggested alternative time slots"
    )
    message: str = Field(default="", description="Conflict message")

    class Config:
        json_schema_extra = {
            "example": {
                "has_conflict": True,
                "conflicting_events": [],
                "suggested_slots": [
                    {"start": "2026-06-13T15:00:00", "end": "2026-06-13T16:00:00", "time_str": "15:00"}
                ],
                "message": "时间冲突，建议改用15:00"
            }
        }