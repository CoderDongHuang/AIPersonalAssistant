"""
Task Planning Prompt Templates

Prompts for generating execution plans based on intent and time reasoning results
"""

TASK_PLANNING_PROMPT = """You are a task planning module for a smart calendar assistant. Based on the recognized intent and parsed time information, generate a detailed execution plan.

Available operations:
1. query_events - Query events in a time range
2. reschedule_event - Move an event to a new time
3. create_event - Create a new calendar event
4. delete_event - Remove an event

Given:
- Intent: {intent}
- Parsed times: {parsed_times}
- Current time: {current_time}

Generate an execution plan in JSON format:
{{
    "action": "operation_type",
    "steps": [
        {{
            "step_number": 1,
            "operation": "description",
            "tool": "calendar" | "email",
            "parameters": {{}}
        }}
    ],
    "fallback_strategy": "What to do if this fails",
    "user_summary": "Brief summary to show the user"
}}

For reschedule_event, the plan should include:
1. Query the source event details
2. Check conflicts at target time
3. Update the event time
4. Send email notification to attendees

For query_events, the plan should:
1. Query events in the specified time range
2. Format and return results

Generate the plan:"""


# System prompt for task planning
PLANNING_SYSTEM_PROMPT = """You are a professional task planning assistant for calendar management.
Your job is to break down high-level calendar operations into concrete, executable steps.
Always consider:
1. Dependency order (check before modify)
2. Error handling (what if the event doesn't exist?)
3. User communication (what should the user be told?)
4. Notification requirements (who needs to be informed?)

Output clean JSON without markdown code fences."""


# Plan templates for common operations
RESCHEDULE_EVENT_PLAN_TEMPLATE = {
    "action": "reschedule_event",
    "steps": [
        {"step_number": 1, "operation": "query_source_event", "tool": "calendar", "parameters": {}},
        {"step_number": 2, "operation": "check_target_conflicts", "tool": "calendar", "parameters": {}},
        {"step_number": 3, "operation": "update_event_time", "tool": "calendar", "parameters": {}},
        {"step_number": 4, "operation": "send_notification", "tool": "email", "parameters": {}},
    ],
    "fallback_strategy": "If source event not found, inform user. If conflicts exist, suggest alternatives.",
    "user_summary": "Reschedule event and notify attendees"
}

CREATE_EVENT_PLAN_TEMPLATE = {
    "action": "create_event",
    "steps": [
        {"step_number": 1, "operation": "check_target_conflicts", "tool": "calendar", "parameters": {}},
        {"step_number": 2, "operation": "create_new_event", "tool": "calendar", "parameters": {}},
        {"step_number": 3, "operation": "send_invitation", "tool": "email", "parameters": {}},
    ],
    "fallback_strategy": "If conflicts exist, suggest alternative times.",
    "user_summary": "Create new event"
}

QUERY_EVENTS_PLAN_TEMPLATE = {
    "action": "query_events",
    "steps": [
        {"step_number": 1, "operation": "list_events_in_range", "tool": "calendar", "parameters": {}},
    ],
    "fallback_strategy": "Return empty result if no events found.",
    "user_summary": "Query calendar events"
}

DELETE_EVENT_PLAN_TEMPLATE = {
    "action": "delete_event",
    "steps": [
        {"step_number": 1, "operation": "find_event", "tool": "calendar", "parameters": {}},
        {"step_number": 2, "operation": "confirm_deletion", "tool": "calendar", "parameters": {}},
        {"step_number": 3, "operation": "notify_cancellation", "tool": "email", "parameters": {}},
    ],
    "fallback_strategy": "If event not found, inform user.",
    "user_summary": "Cancel event and notify attendees"
}
