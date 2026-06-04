"""
自定义异常类
提供清晰的错误层次结构
"""


class AIAssistantError(Exception):
    """AI助理基础异常类"""

    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class CalendarError(AIAssistantError):
    """日历操作异常"""
    pass


class GmailError(AIAssistantError):
    """邮件操作异常"""
    pass


class TimeParsingError(AIAssistantError):
    """时间解析异常"""
    pass


class IntentRecognitionError(AIAssistantError):
    """意图识别异常"""
    pass


class ConflictDetectionError(AIAssistantError):
    """冲突检测异常"""
    pass


class AuthenticationError(AIAssistantError):
    """认证异常"""
    pass


class APIRateLimitError(AIAssistantError):
    """API限流异常"""

    def __init__(self, message: str, retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(message, "RATE_LIMIT_EXCEEDED")