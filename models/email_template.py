"""
Email Template Models

Pydantic models for email templates
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class EmailTemplate(BaseModel):
    """Email template model"""

    subject: str = Field(..., description="Email subject")
    body_text: str = Field(..., description="Plain text body")
    body_html: Optional[str] = Field(default=None, description="HTML body")
    recipients: List[str] = Field(default_factory=list, description="Recipient emails")

    class Config:
        json_schema_extra = {
            "example": {
                "subject": "会议时间变更通知 - 团队周会",
                "body_text": "会议时间已从周三改到周五",
                "body_html": "<html><body>...</body></html>",
                "recipients": ["alice@example.com", "bob@example.com"]
            }
        }

    def render_meeting_change(self, event_title: str, old_time: str,
                             new_time: str, location: str = "") -> None:
        """Render meeting change notification template"""
        self.subject = f"会议时间变更通知 - {event_title}"

        self.body_text = f"""
尊敬的参会人：

会议 "{event_title}" 的时间已调整：

原时间：{old_time}
新时间：{new_time}
地点：{location}

请更新您的日程安排。

此致
AI助理自动通知
        """.strip()

        self.body_html = f"""
<html>
<body style="font-family: Arial, sans-serif;">
    <h2>会议时间变更通知</h2>
    <p>会议 "<strong>{event_title}</strong>" 的时间已调整：</p>
    <ul>
        <li>原时间：{old_time}</li>
        <li>新时间：{new_time}</li>
        <li>地点：{location}</li>
    </ul>
    <p>请更新您的日程安排。</p>
</body>
</html>
        """