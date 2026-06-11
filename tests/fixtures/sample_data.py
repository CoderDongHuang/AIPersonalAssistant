"""
Sample test data fixtures

Provides reusable test data for unit and integration tests
"""

from datetime import datetime, timedelta

# Base reference time: 2026-06-11 (Thursday)
NOW = datetime(2026, 6, 11, 10, 0, 0)

SAMPLE_EVENTS = [
    {
        "id": "evt_001",
        "title": "团队周会",
        "description": "每周团队同步会议，讨论项目进度",
        "location": "会议室A",
        "start_time": (NOW + timedelta(days=2, hours=14)).isoformat(),
        "end_time": (NOW + timedelta(days=2, hours=15)).isoformat(),
        "attendees": ["1218798773@qq.com", "3064801244@qq.com", "1368382140@qq.com"],
        "organizer": "1218798773@qq.com",
    },
    {
        "id": "evt_002",
        "title": "产品评审会议",
        "description": "Q2产品功能评审",
        "location": "线上会议（腾讯会议）",
        "start_time": (NOW + timedelta(days=3, hours=10)).isoformat(),
        "end_time": (NOW + timedelta(days=3, hours=11, minutes=30)).isoformat(),
        "attendees": ["1218798773@qq.com", "3064801244@qq.com"],
        "organizer": "1218798773@qq.com",
    },
    {
        "id": "evt_003",
        "title": "技术分享",
        "description": "LangGraph技术分享会",
        "location": "培训室B",
        "start_time": (NOW + timedelta(days=4, hours=15)).isoformat(),
        "end_time": (NOW + timedelta(days=4, hours=16, minutes=30)).isoformat(),
        "attendees": ["1218798773@qq.com", "3064801244@qq.com", "1368382140@qq.com"],
        "organizer": "1218798773@qq.com",
    },
]

# Intent recognition test cases
INTENT_TEST_CASES = [
    {
        "input": "帮我把下周三下午的会议改到周五",
        "expected_action": "reschedule_event",
    },
    {
        "input": "明天上午我有什么安排？",
        "expected_action": "query_events",
    },
    {
        "input": "添加一个下周一上午10点的产品评审会",
        "expected_action": "create_event",
    },
    {
        "input": "取消后天下午的技术分享",
        "expected_action": "delete_event",
    },
    {
        "input": "查看下周一的日程",
        "expected_action": "query_events",
    },
    {
        "input": "把明天的会议调整到后天",
        "expected_action": "reschedule_event",
    },
    {
        "input": "安排一个明天下午3点的会议",
        "expected_action": "create_event",
    },
]

# Time parsing test cases
TIME_PARSING_TEST_CASES = [
    ("今天", NOW.replace(hour=10, minute=0, second=0, microsecond=0)),
    ("明天", (NOW + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)),
    ("后天", (NOW + timedelta(days=2)).replace(hour=10, minute=0, second=0, microsecond=0)),
    ("今天下午", NOW.replace(hour=14, minute=0, second=0, microsecond=0)),
    ("明天上午", (NOW + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)),
    ("明天晚上", (NOW + timedelta(days=1)).replace(hour=19, minute=0, second=0, microsecond=0)),
]


def get_initial_agent_state(user_input: str) -> dict:
    """Build a minimal AgentState for testing"""
    return {
        "user_input": user_input,
        "intent": None,
        "intent_confidence": 0.0,
        "parsed_times": None,
        "source_time": None,
        "target_time": None,
        "source_event": None,
        "target_slot": None,
        "conflicts": [],
        "conflict_result": None,
        "action_plan": None,
        "execution_results": [],
        "errors": [],
        "email_sent": False,
        "email_recipients": [],
        "response": "",
        "needs_user_confirmation": False,
        "should_continue": False,
    }
