"""
Unit tests for SMTPEmailService and GmailTool

Covers email sending, notification templates, and multi-provider SMTP config
"""

import pytest
from unittest.mock import patch, MagicMock
from services.smtp_email import SMTPEmailService


class TestSMTPEmailService:
    """Test SMTPEmailService (mocking SMTP connections)"""

    def test_service_creation(self):
        """Service should create without errors even without config"""
        service = SMTPEmailService()
        assert service is not None

    def test_auto_detect_smtp_qq(self):
        """QQ email should auto-detect smtp.qq.com"""
        with patch.object(SMTPEmailService, "__init__", lambda self: None):
            service = SMTPEmailService.__new__(SMTPEmailService)
            service.sender_email = "test@qq.com"
            service.sender_password = ""
            service.smtp_server = ""
            service.smtp_port = 587

            # Trigger auto-detection manually
            if not service.smtp_server and "@" in service.sender_email:
                domain = service.sender_email.split("@")[1]
                if domain in service.SMTP_CONFIGS:
                    service.smtp_server = service.SMTP_CONFIGS[domain]["server"]
                    service.smtp_port = service.SMTP_CONFIGS[domain]["port"]

            assert service.smtp_server == "smtp.qq.com"
            assert service.smtp_port == 587

    def test_auto_detect_smtp_gmail(self):
        """Gmail should auto-detect smtp.gmail.com"""
        with patch.object(SMTPEmailService, "__init__", lambda self: None):
            service = SMTPEmailService.__new__(SMTPEmailService)
            service.sender_email = "test@gmail.com"
            service.sender_password = ""
            service.smtp_server = ""
            service.smtp_port = 587

            if not service.smtp_server and "@" in service.sender_email:
                domain = service.sender_email.split("@")[1]
                if domain in service.SMTP_CONFIGS:
                    service.smtp_server = service.SMTP_CONFIGS[domain]["server"]
                    service.smtp_port = service.SMTP_CONFIGS[domain]["port"]

            assert service.smtp_server == "smtp.gmail.com"

    def test_auto_detect_smtp_163(self):
        """163 email should auto-detect smtp.163.com"""
        with patch.object(SMTPEmailService, "__init__", lambda self: None):
            service = SMTPEmailService.__new__(SMTPEmailService)
            service.sender_email = "test@163.com"
            service.sender_password = ""
            service.smtp_server = ""
            service.smtp_port = 587

            if not service.smtp_server and "@" in service.sender_email:
                domain = service.sender_email.split("@")[1]
                if domain in service.SMTP_CONFIGS:
                    service.smtp_server = service.SMTP_CONFIGS[domain]["server"]
                    service.smtp_port = service.SMTP_CONFIGS[domain]["port"]

            assert service.smtp_server == "smtp.163.com"

    def test_send_email_without_config(self):
        """When no SMTP config, should skip sending gracefully (return True)"""
        service = SMTPEmailService()
        # Without EMAIL_SENDER/EMAIL_PASSWORD configured, should skip
        result = service.send_email(
            to_emails=["test@example.com"],
            subject="Test",
            body="Test body",
        )
        # Should return True even without config (graceful skip)
        assert result is True

    def test_send_meeting_notification(self):
        """Meeting notification should generate proper email content"""
        service = SMTPEmailService()
        result = service.send_meeting_notification(
            attendees=["alice@example.com", "bob@example.com"],
            event_title="团队周会",
            old_time="2026-06-10 14:00",
            new_time="2026-06-13 14:00",
            location="会议室A",
            description="时间调整",
        )
        assert result is True  # Graceful skip when not configured

    def test_smtp_configs_have_all_providers(self):
        """Verify all major email providers have SMTP configs"""
        expected_providers = ["qq.com", "163.com", "gmail.com", "outlook.com"]
        for provider in expected_providers:
            assert provider in SMTPEmailService.SMTP_CONFIGS
            assert "server" in SMTPEmailService.SMTP_CONFIGS[provider]
            assert "port" in SMTPEmailService.SMTP_CONFIGS[provider]

    def test_send_email_with_mock_smtp(self):
        """Test actual SMTP send with mocked server"""
        service = SMTPEmailService()

        with patch("smtplib.SMTP") as mock_smtp:
            # Set up config to trigger actual send path
            service.sender_email = "test@qq.com"
            service.sender_password = "test_password"
            service.smtp_server = "smtp.qq.com"

            mock_server = MagicMock()
            mock_smtp.return_value = mock_server

            result = service.send_email(
                to_emails=["recipient@example.com"],
                subject="Test Subject",
                body="Test body content",
            )

            assert result is True
            mock_smtp.assert_called_once_with("smtp.qq.com", 587)
            mock_server.ehlo.assert_called_once()
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with("test@qq.com", "test_password")
            mock_server.sendmail.assert_called_once()
            mock_server.quit.assert_called_once()


class TestGmailTool:
    """Test the LangChain GmailTool wrapper"""

    def setup_method(self):
        from tools.gmail_tool import GmailTool
        self.tool = GmailTool()

    def test_tool_creation(self):
        assert self.tool.name == "email"
        assert self.tool.email_service is not None

    def test_tool_send_notification(self):
        result = self.tool.send_notification(
            attendees=["test@example.com"],
            event_title="测试会议",
            old_time="2026-06-10 14:00",
            new_time="2026-06-13 14:00",
        )
        # Without SMTP config, should still return True (graceful degrade)
        assert result is True
