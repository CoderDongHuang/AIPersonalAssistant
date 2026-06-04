"""
格式化工具函数
"""

from datetime import datetime
from typing import Optional


def format_datetime(dt: datetime, include_seconds: bool = False) -> str:
    """
    格式化日期时间为可读字符串

    Args:
        dt: datetime对象
        include_seconds: 是否包含秒

    Returns:
        str: 格式化后的时间字符串
    """
    if include_seconds:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return dt.strftime("%Y-%m-%d %H:%M")


def format_date_range(start: datetime, end: datetime) -> str:
    """
    格式化时间范围

    Args:
        start: 开始时间
        end: 结束时间

    Returns:
        str: 格式化后的时间范围
    """
    start_str = format_datetime(start)
    end_str = format_datetime(end)
    return f"{start_str} - {end_str}"


def format_duration(minutes: int) -> str:
    """
    格式化时长

    Args:
        minutes: 分钟数

    Returns:
        str: 格式化后的时长，如 "2小时30分钟"
    """
    hours = minutes // 60
    mins = minutes % 60

    if hours == 0:
        return f"{mins}分钟"
    elif mins == 0:
        return f"{hours}小时"
    else:
        return f"{hours}小时{mins}分钟"


def pretty_print_event(event_data: dict) -> str:
    """
    美观地打印事件信息

    Args:
        event_data: 事件数据字典

    Returns:
        str: 格式化后的事件描述
    """
    lines = [
        f"📅 事件: {event_data.get('title', '未知')}",
        f"⏰ 时间: {format_date_range(event_data['start'], event_data['end'])}",
        f"📍 地点: {event_data.get('location', '未指定')}",
        f"👥 参会人: {', '.join(event_data.get('attendees', []))}",
    ]

    if event_data.get('description'):
        lines.append(f"📝 描述: {event_data['description']}")

    return "\n".join(lines)