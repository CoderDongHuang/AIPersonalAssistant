"""
Gmail Tool

Wrapper for SMTPEmailService with LangChain tool interface
"""

from typing import List
from langchain.tools import BaseTool
from services.smtp_email import SMTPEmailService
from loguru import logger


class GmailTool(BaseTool):
    """Email tool for LangChain/LangGraph"""

    name: str = "email"
    description: str = "发送邮件通知"

    def __init__(self):
        super().__init__()
        self.email_service = SMTPEmailService()

    def _run(self, query: str) -> str:
        """Execute email operation"""
        try:
            return f"Email sent: {query}"
        except Exception as e:
            logger.error(f"Email tool error: {e}")
            return f"Error: {str(e)}"

    async def _arun(self, query: str) -> str:
        """Async version"""
        return self._run(query)

    def send_notification(self, attendees: List[str], event_title: str,
                         old_time: str, new_time: str) -> bool:
        """Send meeting change notification"""
        return self.email_service.send_meeting_notification(
            attendees, event_title, old_time, new_time
        )


# Global instance
gmail_tool = GmailTool()