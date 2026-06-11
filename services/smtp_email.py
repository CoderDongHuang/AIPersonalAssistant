"""
SMTP Email Service

Send emails using SMTP protocol
Supports QQ Mail, 163 Mail, Gmail, etc.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from loguru import logger
from config.settings import settings
from utils.validators import validate_emails


class SMTPEmailService:
    """SMTP email service"""

    # SMTP server configurations
    SMTP_CONFIGS = {
        'qq.com': {'server': 'smtp.qq.com', 'port': 587},
        '163.com': {'server': 'smtp.163.com', 'port': 587},
        'gmail.com': {'server': 'smtp.gmail.com', 'port': 587},
        'outlook.com': {'server': 'smtp-mail.outlook.com', 'port': 587},
    }

    def __init__(self):
        """Initialize email service"""
        self.sender_email = getattr(settings, 'EMAIL_SENDER', '')
        self.sender_password = getattr(settings, 'EMAIL_PASSWORD', '')
        self.smtp_server = getattr(settings, 'EMAIL_SMTP_SERVER', '')
        self.smtp_port = getattr(settings, 'EMAIL_SMTP_PORT', 587)

        # Auto-detect SMTP server from email domain if not configured
        if not self.smtp_server and '@' in self.sender_email:
            domain = self.sender_email.split('@')[1]
            if domain in self.SMTP_CONFIGS:
                self.smtp_server = self.SMTP_CONFIGS[domain]['server']
                self.smtp_port = self.SMTP_CONFIGS[domain]['port']

        logger.info("SMTPEmailService initialized")
        logger.debug(f"Sender: {self.sender_email}")
        logger.debug(f"SMTP Server: {self.smtp_server}:{self.smtp_port}")

    def send_email(self, to_emails: List[str], subject: str,
                   body: str, html_body: Optional[str] = None) -> bool:
        """
        Send email via SMTP

        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            body: Plain text body
            html_body: HTML body (optional)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.sender_email or not self.sender_password:
            logger.warning("⚠️  Email not configured, skipping send")
            logger.info("📧 Email content (not sent):")
            logger.info(f"   To: {to_emails}")
            logger.info(f"   Subject: {subject}")
            logger.info(f"   Body: {body[:100]}...")
            return True  # Return True to not block workflow

        # Validate recipient emails
        valid_emails, invalid_emails = validate_emails(to_emails)
        if invalid_emails:
            logger.warning(f"⚠️  Invalid email addresses skipped: {invalid_emails}")
        if not valid_emails:
            logger.error("❌ No valid recipient email addresses")
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(valid_emails)
            msg['Subject'] = subject

            # Add plain text body
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            # Add HTML body if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html', 'utf-8'))

            # Connect to SMTP server
            logger.info(f"Connecting to SMTP: {self.smtp_server}:{self.smtp_port}")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.ehlo()
            server.starttls()
            server.login(self.sender_email, self.sender_password)

            # Send email
            server.sendmail(self.sender_email, valid_emails, msg.as_string())
            server.quit()

            logger.info(f"✅ Email sent to {len(valid_emails)} recipients")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            logger.warning("Continuing without email notification")
            return False

    def send_meeting_notification(self, attendees: List[str],
                                  event_title: str,
                                  old_time: str,
                                  new_time: str,
                                  location: str = "",
                                  description: str = "") -> bool:
        """
        Send meeting change notification

        Args:
            attendees: List of attendee emails
            event_title: Meeting title
            old_time: Original meeting time
            new_time: New meeting time
            location: Meeting location
            description: Meeting description

        Returns:
            True if sent successfully
        """
        subject = f"会议时间变更通知 - {event_title}"

        body = f"""
尊敬的参会人：

您好！

会议 "{event_title}" 的时间已调整，详情如下：

📅 原时间：{old_time}
📅 新时间：{new_time}
📍 地点：{location}
📝 说明：{description}

请更新您的日程安排。如有问题，请及时联系会议组织者。

此致
敬礼

AI助理自动通知
        """.strip()

        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
            📅 会议时间变更通知
        </h2>
        
        <p>尊敬的参会人：</p>
        
        <p>您好！会议 "<strong>{event_title}</strong>" 的时间已调整，详情如下：</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0;">
            <p><strong>📅 原时间：</strong>{old_time}</p>
            <p><strong>📅 新时间：</strong>{new_time}</p>
            <p><strong>📍 地点：</strong>{location}</p>
            <p><strong>📝 说明：</strong>{description}</p>
        </div>
        
        <p>请更新您的日程安排。如有问题，请及时联系会议组织者。</p>
        
        <p style="margin-top: 30px; color: #7f8c8d;">
            此致<br>
            敬礼<br><br>
            AI助理自动通知
        </p>
    </div>
</body>
</html>
        """

        logger.info(f"Sending meeting notification to {len(attendees)} attendees")
        return self.send_email(attendees, subject, body, html_body)


# Global instance
smtp_email = SMTPEmailService()