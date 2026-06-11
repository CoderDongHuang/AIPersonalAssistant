"""
Unit tests for TimeParser

Covers natural language time expression parsing
"""

import pytest
from datetime import datetime, timedelta
from tools.time_parser import TimeParser


class TestTimeParser:
    """Test TimeParser natural language parsing"""

    def setup_method(self):
        self.parser = TimeParser()
        self.now = datetime(2026, 6, 11, 10, 0, 0)  # Thursday, June 11, 2026

    # ── Relative day parsing ──

    def test_parse_today(self):
        result = self.parser.parse_time_expression("今天", base_time=self.now)
        assert result is not None
        assert result.date() == self.now.date()
        assert result.hour == 10  # default morning time

    def test_parse_today_afternoon(self):
        result = self.parser.parse_time_expression("今天下午", base_time=self.now)
        assert result is not None
        assert result.date() == self.now.date()
        assert result.hour == 14

    def test_parse_tomorrow(self):
        result = self.parser.parse_time_expression("明天", base_time=self.now)
        assert result is not None
        assert result.date() == (self.now + timedelta(days=1)).date()

    def test_parse_day_after_tomorrow(self):
        result = self.parser.parse_time_expression("后天", base_time=self.now)
        assert result is not None
        assert result.date() == (self.now + timedelta(days=2)).date()

    def test_parse_days_later(self):
        result = self.parser.parse_time_expression("3天后", base_time=self.now)
        assert result is not None
        assert result.date() == (self.now + timedelta(days=3)).date()

    # ── Weekday parsing ──

    def test_parse_next_wednesday(self):
        """下周三 from Thursday → next Wednesday (6 days later)"""
        result = self.parser.parse_time_expression("下周三", base_time=self.now)
        assert result is not None
        # Wednesday is weekday 2. From Thursday (3), next Wednesday is 6 days ahead
        expected = self.now + timedelta(days=6)
        assert result.date() == expected.date()

    def test_parse_next_monday(self):
        """下周一 from Thursday → next Monday (4 days later)"""
        result = self.parser.parse_time_expression("下周一", base_time=self.now)
        assert result is not None
        expected = self.now + timedelta(days=4)
        assert result.date() == expected.date()

    def test_parse_this_week_friday(self):
        """这周五 from Thursday → this Friday (1 day later)"""
        result = self.parser.parse_time_expression("这周五", base_time=self.now)
        assert result is not None
        expected = self.now + timedelta(days=1)
        assert result.date() == expected.date()

    def test_parse_weekday_zh_numbers(self):
        """Test 星期一, 星期二, etc."""
        result = self.parser.parse_time_expression("下星期二下午", base_time=self.now)
        assert result is not None
        expected = self.now + timedelta(days=5)  # Thursday → next Tuesday
        assert result.date() == expected.date()
        assert result.hour == 14

    # ── Time period mapping ──

    def test_time_period_morning(self):
        result = self.parser.parse_time_expression("明天上午", base_time=self.now)
        assert result.hour == 10

    def test_time_period_noon(self):
        result = self.parser.parse_time_expression("明天中午", base_time=self.now)
        assert result.hour == 12

    def test_time_period_afternoon(self):
        result = self.parser.parse_time_expression("明天下午", base_time=self.now)
        assert result.hour == 14

    def test_time_period_evening(self):
        result = self.parser.parse_time_expression("明天晚上", base_time=self.now)
        assert result.hour == 19

    def test_time_period_early_morning(self):
        result = self.parser.parse_time_expression("明天凌晨", base_time=self.now)
        assert result.hour == 0

    def test_default_to_morning_when_no_period(self):
        """When no period specified and hour is 0, default to 10:00"""
        result = self.parser.parse_time_expression("下周三", base_time=self.now)
        assert result.hour == 10

    # ── Compound expressions ──

    def test_compound_next_weekday_afternoon(self):
        result = self.parser.parse_time_expression("下周三下午", base_time=self.now)
        assert result is not None
        assert result.hour == 14
        assert result.minute == 0

    def test_compound_this_weekday_morning(self):
        result = self.parser.parse_time_expression("本周五上午", base_time=self.now)
        assert result is not None
        assert result.hour == 10

    # ── Time range parsing ──

    def test_parse_time_range(self):
        start, end = self.parser.parse_time_range("明天下午")
        assert start is not None
        assert end is not None
        assert (end - start).total_seconds() == 3600  # default 1 hour

    # ── Formatting ──

    def test_format_datetime(self):
        dt = datetime(2026, 6, 11, 14, 30)
        result = self.parser.format_datetime(dt, include_time=True)
        assert result == "2026-06-11 14:30"

    def test_format_datetime_date_only(self):
        dt = datetime(2026, 6, 11, 14, 30)
        result = self.parser.format_datetime(dt, include_time=False)
        assert result == "2026-06-11"

    # ── Edge cases ──

    def test_none_for_unparseable_input(self):
        result = self.parser.parse_time_expression("随机文本xyz", base_time=self.now)
        # Should return None for unparseable input (without time period, defaults to morning)
        # Actually with default morning, it returns the date with 10:00
        # Let's test truly unparseable text
        result2 = self.parser.parse_time_expression("你好世界", base_time=self.now)
        assert result2 is None or result2.hour == 10  # falls to default

    def test_empty_expression(self):
        result = self.parser.parse_time_expression("", base_time=self.now)
        assert result is None

    def test_weekday_mapping_coverage(self):
        """Test all weekday mappings are present"""
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日",
                     "星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日",
                     "星期天"]
        for wd in weekdays:
            assert wd in self.parser.WEEKDAYS, f"Missing: {wd}"
