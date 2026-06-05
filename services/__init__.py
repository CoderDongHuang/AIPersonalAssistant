"""
Business Services Module

Provides high-level business logic encapsulation
"""

from services.local_calendar import LocalCalendarService, local_calendar
from services.smtp_email import SMTPEmailService, smtp_email

__all__ = [
    "LocalCalendarService",
    "local_calendar",
    "SMTPEmailService",
    "smtp_email"
]
