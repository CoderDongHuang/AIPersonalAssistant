"""
Unit tests for utils module — validators, formatters, exceptions
"""

import pytest
from datetime import datetime

from utils.validators import (
    validate_email, validate_emails, validate_event_title, validate_timezone,
)
from utils.formatters import (
    format_datetime, format_date_range, format_duration, pretty_print_event,
)
from utils.exceptions import (
    AIAssistantError, CalendarError, GmailError, TimeParsingError,
    IntentRecognitionError, ConflictDetectionError, AuthenticationError,
    APIRateLimitError,
)


class TestValidators:
    """Test data validation utilities"""

    # ── Email validation ──

    def test_validate_email_valid(self):
        assert validate_email("test@example.com") is True
        assert validate_email("user.name+tag@domain.co.jp") is True
        assert validate_email("1218798773@qq.com") is True

    def test_validate_email_invalid(self):
        assert validate_email("") is False
        assert validate_email("not-an-email") is False
        assert validate_email("@domain.com") is False
        assert validate_email("user@") is False
        assert validate_email("user@.com") is False

    def test_validate_emails_batch(self):
        valid, invalid = validate_emails([
            "a@test.com", "b@test.com", "invalid", "c@test.com",
        ])
        assert valid == ["a@test.com", "b@test.com", "c@test.com"]
        assert invalid == ["invalid"]

    def test_validate_emails_all_invalid(self):
        valid, invalid = validate_emails(["bad1", "bad2"])
        assert valid == []
        assert invalid == ["bad1", "bad2"]

    def test_validate_emails_empty_list(self):
        valid, invalid = validate_emails([])
        assert valid == []
        assert invalid == []

    # ── Event title validation ──

    def test_validate_event_title_valid(self):
        assert validate_event_title("团队周会") is True
        assert validate_event_title("A") is True

    def test_validate_event_title_empty(self):
        assert validate_event_title("") is False
        assert validate_event_title("   ") is False

    def test_validate_event_title_too_long(self):
        assert validate_event_title("X" * 256, max_length=255) is False

    # ── Timezone validation ──

    def test_validate_timezone_valid(self):
        assert validate_timezone("Asia/Shanghai") is True
        assert validate_timezone("America/New_York") is True
        assert validate_timezone("UTC") is True

    def test_validate_timezone_invalid(self):
        assert validate_timezone("Mars/BaseOne") is False
        assert validate_timezone("not-a-tz") is False


class TestFormatters:
    """Test formatting utilities"""

    def test_format_datetime(self):
        dt = datetime(2026, 6, 15, 14, 30, 45)
        assert format_datetime(dt) == "2026-06-15 14:30"
        assert format_datetime(dt, include_seconds=True) == "2026-06-15 14:30:45"

    def test_format_date_range(self):
        start = datetime(2026, 6, 15, 14, 0)
        end = datetime(2026, 6, 15, 15, 30)
        result = format_date_range(start, end)
        assert "2026-06-15 14:00" in result
        assert "15:30" in result

    def test_format_duration(self):
        assert format_duration(0) == "0分钟"
        assert format_duration(30) == "30分钟"
        assert format_duration(60) == "1小时"
        assert format_duration(90) == "1小时30分钟"
        assert format_duration(120) == "2小时"

    def test_pretty_print_event(self):
        event = {
            "title": "团队周会",
            "start": datetime(2026, 6, 15, 14, 0),
            "end": datetime(2026, 6, 15, 15, 0),
            "location": "会议室A",
            "attendees": ["alice@test.com", "bob@test.com"],
            "description": "周报同步",
        }
        result = pretty_print_event(event)
        assert "团队周会" in result
        assert "14:00" in result
        assert "15:00" in result
        assert "会议室A" in result
        assert "alice@test.com" in result
        assert "周报同步" in result

    def test_pretty_print_event_minimal(self):
        event = {
            "title": "简单会议",
            "start": datetime(2026, 6, 15, 14, 0),
            "end": datetime(2026, 6, 15, 15, 0),
            "attendees": [],
        }
        result = pretty_print_event(event)
        assert "简单会议" in result
        assert "未指定" in result  # No location


class TestCustomExceptions:
    """Test custom exception hierarchy"""

    def test_base_error(self):
        err = AIAssistantError("test", error_code="TEST")
        assert str(err) == "test"
        assert err.error_code == "TEST"
        assert err.message == "test"

    def test_calendar_error(self):
        err = CalendarError("calendar error")
        assert isinstance(err, AIAssistantError)
        assert isinstance(err, CalendarError)

    def test_gmail_error(self):
        err = GmailError("email error")
        assert isinstance(err, AIAssistantError)

    def test_time_parsing_error(self):
        err = TimeParsingError("time error")
        assert isinstance(err, AIAssistantError)

    def test_intent_recognition_error(self):
        err = IntentRecognitionError("intent error")
        assert isinstance(err, AIAssistantError)

    def test_conflict_detection_error(self):
        err = ConflictDetectionError("conflict error")
        assert isinstance(err, AIAssistantError)

    def test_auth_error(self):
        err = AuthenticationError("auth error")
        assert isinstance(err, AIAssistantError)

    def test_rate_limit_error(self):
        err = APIRateLimitError("rate limit", retry_after=30)
        assert err.error_code == "RATE_LIMIT_EXCEEDED"
        assert err.retry_after == 30
        assert isinstance(err, AIAssistantError)
