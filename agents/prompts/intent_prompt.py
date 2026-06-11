"""
Intent Recognition Prompt Templates

Prompts for natural language intent parsing
"""

INTENT_RECOGNITION_PROMPT = """You are an intent recognition module for a smart calendar assistant. Analyze user input and identify their intent.

Supported intent types:
1. query_events - Query calendar events (e.g., "What's on my schedule tomorrow?", "明天有什么安排？")
2. reschedule_event - Reschedule a meeting (e.g., "Move Wednesday's meeting to Friday", "把周三的会议改到周五")
3. create_event - Create a new event (e.g., "Schedule a meeting next Monday at 10am", "下周一上午10点开会")
4. update_event - Update event details (e.g., "Change the meeting room to A", "把会议室改成A")
5. delete_event - Delete/cancel an event (e.g., "Cancel tomorrow's meeting", "取消明天的会议")

Output JSON format:
{{
    "action": "intent_type",
    "confidence": 0.0-1.0,
    "parameters": {{
        "event_name": "Event name (if present)",
        "source_time": "Original time description (if rescheduling)",
        "target_time": "Target time description (if rescheduling)",
        "date": "Date description",
        "time": "Time description",
        "attendees": ["List of attendees"],
        "location": "Location"
    }}
}}

User input: {user_input}

Analyze and output JSON:"""


# System prompt for the intent recognition role
INTENT_SYSTEM_PROMPT = """You are a professional intent recognition assistant. Only output valid JSON results.
Focus on accurately identifying the user's calendar-related intent from their natural language input.
For Chinese input, pay special attention to time-related keywords like:
- 明天 (tomorrow), 后天 (day after), 下周 (next week), 这周 (this week)
- 上午 (morning), 下午 (afternoon), 晚上 (evening)
- 改到/移到 (reschedule to), 取消 (cancel), 查看 (query)

Always output clean JSON without markdown code fences."""


# Few-shot examples for better accuracy
FEW_SHOT_EXAMPLES = [
    {
        "input": "帮我把下周三下午的会议改到周五",
        "output": {
            "action": "reschedule_event",
            "confidence": 0.95,
            "parameters": {
                "action": "reschedule_event",
                "event_name": "会议",
                "source_time": "下周三下午",
                "target_time": "周五"
            }
        }
    },
    {
        "input": "明天上午我有什么安排？",
        "output": {
            "action": "query_events",
            "confidence": 0.95,
            "parameters": {
                "action": "query_events",
                "date": "明天上午"
            }
        }
    },
    {
        "input": "下周一上午10点开产品评审会",
        "output": {
            "action": "create_event",
            "confidence": 0.90,
            "parameters": {
                "action": "create_event",
                "event_name": "产品评审会",
                "date": "下周一",
                "time": "上午10点"
            }
        }
    },
    {
        "input": "取消后天下午的技术分享",
        "output": {
            "action": "delete_event",
            "confidence": 0.90,
            "parameters": {
                "action": "delete_event",
                "event_name": "技术分享",
                "source_time": "后天下午"
            }
        }
    },
]
