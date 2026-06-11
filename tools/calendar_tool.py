"""
Calendar Tool

Wrapper for LocalCalendarService with LangChain tool interface
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from langchain.tools import BaseTool
from services.local_calendar import LocalCalendarService
from tools.time_parser import TimeParser
from loguru import logger


class CalendarTool(BaseTool):
    """Calendar tool for LangChain/LangGraph"""

    name: str = "calendar"
    description: str = "查询、创建、更新日历事件"
    calendar_service: LocalCalendarService = None
    time_parser: TimeParser = None

    def __init__(self):
        # Initialize services first
        object.__setattr__(self, 'calendar_service', LocalCalendarService())
        object.__setattr__(self, 'time_parser', TimeParser())
        # Then call parent __init__
        super().__init__()

    def _run(self, query: str) -> str:
        """Execute calendar operation"""
        try:
            # This is a simplified version
            # In real implementation, parse query and call appropriate methods
            return f"Calendar query executed: {query}"
        except Exception as e:
            logger.error(f"Calendar tool error: {e}")
            return f"Error: {str(e)}"

    async def _arun(self, query: str) -> str:
        """Async version"""
        return self._run(query)

    def list_events(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """List events in time range"""
        return self.calendar_service.list_events(start_time, end_time)

    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get single event"""
        return self.calendar_service.get_event(event_id)

    def update_event(self, event_id: str, updates: Dict[str, Any]) -> bool:
        """Update event"""
        return self.calendar_service.update_event(event_id, updates)

    def check_conflicts(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Check for conflicts"""
        return self.calendar_service.check_conflicts(start_time, end_time)


# Global instance - delay initialization to avoid circular imports
_calendar_tool_instance = None

def get_calendar_tool():
    """Get or create CalendarTool instance"""
    global _calendar_tool_instance
    if _calendar_tool_instance is None:
        _calendar_tool_instance = CalendarTool()
    return _calendar_tool_instance
