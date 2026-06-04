"""
数据验证工具函数
"""

from typing import List, Optional
import re


def validate_email(email: str) -> bool:
    """
    验证邮箱格式

    Args:
        email: 邮箱地址

    Returns:
        bool: 是否为有效邮箱
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_emails(emails: List[str]) -> tuple[List[str], List[str]]:
    """
    批量验证邮箱列表

    Args:
        emails: 邮箱地址列表

    Returns:
        tuple: (有效邮箱列表, 无效邮箱列表)
    """
    valid_emails = []
    invalid_emails = []

    for email in emails:
        if validate_email(email):
            valid_emails.append(email)
        else:
            invalid_emails.append(email)

    return valid_emails, invalid_emails


def validate_event_title(title: str, max_length: int = 255) -> bool:
    """
    验证事件标题

    Args:
        title: 事件标题
        max_length: 最大长度

    Returns:
        bool: 是否有效
    """
    if not title or not title.strip():
        return False
    if len(title) > max_length:
        return False
    return True


def validate_timezone(timezone: str) -> bool:
    """
    验证时区字符串

    Args:
        timezone: 时区名称，如 'Asia/Shanghai'

    Returns:
        bool: 是否有效
    """
    import pytz
    try:
        pytz.timezone(timezone)
        return True
    except pytz.exceptions.UnknownTimeZoneError:
        return False