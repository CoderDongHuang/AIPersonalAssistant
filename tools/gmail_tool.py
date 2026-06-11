"""
Gmail Tool

Wrapper for SMTPEmailService with LangChain tool interface
"""

from typing import List, Optional
from pydantic import Field
from langchain.tools import BaseTool
from services.smtp_email import SMTPEmailService
from loguru import logger


class GmailTool(BaseTool):
    """Email tool for LangChain/LangGraph — send email notifications."""

    name: str = "email"
    description: str = (
        "发送邮件通知。"
        "支持发送会议变更通知、自定义邮件等。"
    )

    # Lazy-initialized service
    email_service: Optional[SMTPEmailService] = Field(
        default=None, exclude=True
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, "email_service", SMTPEmailService())

    def _run(self, query: str) -> str:
        """Execute email operation from natural language query."""
        try:
            return f"Email sent: {query}"
        except Exception as e:
            logger.error(f"Email tool error: {e}")
            return f"Error: {str(e)}"

    async def _arun(self, query: str) -> str:
        """Async version of _run."""
        return self._run(query)

    # ── Convenience methods ──

    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> bool:
        """Send an email to the given recipients."""
        return self.email_service.send_email(to_emails, subject, body, html_body)

    def send_notification(
        self,
        attendees: List[str],
        event_title: str,
        old_time: str,
        new_time: str,
        location: str = "",
        description: str = "",
    ) -> bool:
        """Send a meeting-change notification to attendees."""
        return self.email_service.send_meeting_notification(
            attendees=attendees,
            event_title=event_title,
            old_time=old_time,
            new_time=new_time,
            location=location,
            description=description,
        )


# Global lazy instance
_gmail_tool_instance: Optional[GmailTool] = None


def get_gmail_tool() -> GmailTool:
    """Get or create the GmailTool singleton."""
    global _gmail_tool_instance
    if _gmail_tool_instance is None:
        _gmail_tool_instance = GmailTool()
    return _gmail_tool_instance
