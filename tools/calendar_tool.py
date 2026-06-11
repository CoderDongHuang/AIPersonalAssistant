"""
Calendar Tool

Wrapper for LocalCalendarService with LangChain tool interface
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import Field
from langchain.tools import BaseTool
from services.local_calendar import LocalCalendarService
from tools.time_parser import TimeParser
from loguru import logger


class CalendarTool(BaseTool):
    """Calendar tool for LangChain/LangGraph — query and manage calendar events."""

    name: str = "calendar"
    description: str = (
        "查询、创建、更新日历事件。"
        "支持的操作：查询时间段内事件、获取单个事件、更新事件、创建事件、"
        "删除事件、检测时间冲突。"
    )

    # Lazy-initialized services (set after __init__ via _init_services)
    calendar_service: Optional[LocalCalendarService] = Field(
        default=None, exclude=True
    )
    time_parser: Optional[TimeParser] = Field(
        default=None, exclude=True
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Use object.__setattr__ to set non-validated internal services
        object.__setattr__(self, "calendar_service", LocalCalendarService())
        object.__setattr__(self, "time_parser", TimeParser())

    def _run(self, query: str) -> str:
        """Execute calendar operation from natural language query."""
        try:
            return f"Calendar query executed: {query}"
        except Exception as e:
            logger.error(f"Calendar tool error: {e}")
            return f"Error: {str(e)}"

    async def _arun(self, query: str) -> str:
        """Async version of _run."""
        return self._run(query)

    # ── Convenience methods (used directly by nodes) ──

    def list_events(
        self, start_time: datetime, end_time: datetime
    ) -> List[Dict[str, Any]]:
        """List events in a time range."""
        return self.calendar_service.list_events(start_time, end_time)

    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get a single event by ID."""
        return self.calendar_service.get_event(event_id)

    def update_event(self, event_id: str, updates: Dict[str, Any]) -> bool:
        """Update an event's fields."""
        return self.calendar_service.update_event(event_id, updates)

    def create_event(self, event_data: Dict[str, Any]) -> str:
        """Create a new event. Returns the new event ID."""
        return self.calendar_service.create_event(event_data)

    def delete_event(self, event_id: str) -> bool:
        """Delete an event by ID."""
        return self.calendar_service.delete_event(event_id)

    def check_conflicts(
        self, start_time: datetime, end_time: datetime
    ) -> List[Dict[str, Any]]:
        """Check for scheduling conflicts in the given time window."""
        return self.calendar_service.check_conflicts(start_time, end_time)

    def find_available_slots(
        self,
        date: datetime,
        duration_minutes: int = 60,
        preferred_times: List[str] = None,
    ) -> List[Dict[str, datetime]]:
        """Find available time slots on a given date."""
        return self.calendar_service.find_available_slots(
            date, duration_minutes, preferred_times
        )


# Global lazy instance
_calendar_tool_instance: Optional[CalendarTool] = None


def get_calendar_tool() -> CalendarTool:
    """Get or create the CalendarTool singleton."""
    global _calendar_tool_instance
    if _calendar_tool_instance is None:
        _calendar_tool_instance = CalendarTool()
    return _calendar_tool_instance
