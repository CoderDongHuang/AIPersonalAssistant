"""
Email Template Models

Pydantic v2 models for email templates and meeting notifications
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional


class EmailTemplate(BaseModel):
    """Email template model"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "subject": "会议时间变更通知 - 团队周会",
                "body_text": "会议时间已从周三改到周五",
                "body_html": "<html><body>...</body></html>",
                "recipients": ["alice@example.com", "bob@example.com"],
            }
        }
    )

    subject: str = Field(..., description="Email subject")
    body_text: str = Field(..., description="Plain text body")
    body_html: Optional[str] = Field(default=None, description="HTML body")
    recipients: List[str] = Field(default_factory=list, description="Recipient emails")

    @classmethod
    def create_meeting_change_notification(
        cls,
        event_title: str,
        old_time: str,
        new_time: str,
        location: str = "",
        description: str = "",
        recipients: Optional[List[str]] = None,
    ) -> "EmailTemplate":
        """
        Create a meeting-change notification template (factory method).

        Returns a NEW EmailTemplate instance — does NOT mutate any existing object.
        """
        subject = f"会议时间变更通知 - {event_title}"

        body_text = f"""
尊敬的参会人：

您好！

会议 "{event_title}" 的时间已调整，详情如下：

📅 原时间：{old_time}
📅 新时间：{new_time}
📍 地点：{location or '未指定'}
📝 说明：{description or '无'}

请更新您的日程安排。如有问题，请及时联系会议组织者。

此致
敬礼

AI助理自动通知
        """.strip()

        body_html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db;">
            📅 会议时间变更通知
        </h2>
        <p>尊敬的参会人：</p>
        <p>您好！会议 "<strong>{event_title}</strong>" 的时间已调整，详情如下：</p>
        <div style="background-color: #f8f9fa; padding: 15px;
                    border-left: 4px solid #3498db; margin: 20px 0;">
            <p><strong>📅 原时间：</strong>{old_time}</p>
            <p><strong>📅 新时间：</strong>{new_time}</p>
            <p><strong>📍 地点：</strong>{location or '未指定'}</p>
            <p><strong>📝 说明：</strong>{description or '无'}</p>
        </div>
        <p>请更新您的日程安排。如有问题，请及时联系会议组织者。</p>
        <p style="margin-top: 30px; color: #7f8c8d;">
            此致<br>敬礼<br><br>AI助理自动通知
        </p>
    </div>
</body>
</html>
        """

        return cls(
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            recipients=recipients or [],
        )
