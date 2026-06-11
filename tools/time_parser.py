"""
Time Parser Tool

Parse natural language time expressions to datetime objects
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
import re
from loguru import logger


class TimeParser:
    """Natural language time parser"""

    # Time period mappings
    TIME_PERIODS = {
        '早上': ('09:00', 'morning'),
        '上午': ('10:00', 'morning'),
        '中午': ('12:00', 'noon'),
        '下午': ('14:00', 'afternoon'),
        '晚上': ('19:00', 'evening'),
        '凌晨': ('00:00', 'early_morning'),
    }

    # Day of week mappings
    WEEKDAYS = {
        '周一': 0, '星期一': 0,
        '周二': 1, '星期二': 1,
        '周三': 2, '星期三': 2,
        '周四': 3, '星期四': 3,
        '周五': 4, '星期五': 4,
        '周六': 5, '星期六': 5,
        '周日': 6, '星期天': 6, '星期日': 6,
    }

    def parse_time_expression(self, expression: str,
                             base_time: datetime = None) -> Optional[datetime]:
        """
        Parse natural language time expression

        Args:
            expression: Time expression like "下周三下午"
            base_time: Base time for relative calculations

        Returns:
            Parsed datetime or None
        """
        if base_time is None:
            base_time = datetime.now()

        logger.debug(f"Parsing time expression: {expression}")

        # Try different parsing strategies
        dt = self._parse_relative_date(expression, base_time)

        if dt is None:
            logger.warning(f"Failed to parse time expression: {expression}")
            return None

        # Apply time period if present
        dt = self._apply_time_period(expression, dt)

        logger.info(f"Parsed '{expression}' -> {dt}")
        return dt

    def _parse_relative_date(self, expression: str,
                            base_time: datetime) -> Optional[datetime]:
        """Parse relative date expressions"""

        # "今天" / "明天" / "后天"
        if '今天' in expression:
            return base_time.replace(hour=0, minute=0, second=0, microsecond=0)
        elif '明天' in expression:
            return (base_time + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif '后天' in expression:
            return (base_time + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)

        # "下周X" / "这周X" / "周X"
        week_match = re.search(r'(?:下|这|本)?周([一二三四五六日])', expression)
        if week_match:
            weekday_str = week_match.group(1)
            weekday = self.WEEKDAYS.get(f'周{weekday_str}')

            if weekday is not None:
                current_weekday = base_time.weekday()
                days_ahead = weekday - current_weekday

                if '下周' in expression:
                    days_ahead += 7
                elif '这周' in expression or '本周' in expression:
                    if days_ahead <= 0:
                        days_ahead += 7
                else:
                    # Just "周X" - assume next occurrence
                    if days_ahead <= 0:
                        days_ahead += 7

                target_date = base_time + timedelta(days=days_ahead)
                return target_date.replace(hour=0, minute=0, second=0, microsecond=0)

        # "X天后"
        days_match = re.search(r'(\d+)天后', expression)
        if days_match:
            days = int(days_match.group(1))
            return (base_time + timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)

        return None


    def _apply_time_period(self, expression: str, dt: datetime) -> datetime:
        """Apply time period (morning, afternoon, etc.) to datetime"""

        for period, (time_str, _) in self.TIME_PERIODS.items():
            if period in expression:
                hour, minute = map(int, time_str.split(':'))
                return dt.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # Default to morning if no period specified
        if dt.hour == 0:
            return dt.replace(hour=10, minute=0, second=0, microsecond=0)

        return dt

    def parse_time_range(self, expression: str) -> Tuple[Optional[datetime], Optional[datetime]]:
        """
        Parse time range expression

        Returns:
            Tuple of (start_time, end_time)
        """
        # Simple implementation - can be extended
        start = self.parse_time_expression(expression)

        if start:
            # Default 1 hour duration
            end = start + timedelta(hours=1)
            return start, end

        return None, None

    def format_datetime(self, dt: datetime, include_time: bool = True) -> str:
        """Format datetime to readable string"""
        if include_time:
            return dt.strftime("%Y-%m-%d %H:%M")
        return dt.strftime("%Y-%m-%d")


# Global instance
time_parser = TimeParser()