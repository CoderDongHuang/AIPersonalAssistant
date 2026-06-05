"""
Agent State Model

LangGraph state definition for the AI assistant
"""

from typing import TypedDict, List, Optional, Dict, Any
from models.calendar_event import CalendarEvent, TimeSlot, ConflictResult


class AgentState(TypedDict):
    """
    Agent state for LangGraph workflow

    Represents the complete state of the agent during execution
    """

    # User input
    user_input: str

    # Parsed intent
    intent: Optional[Dict[str, Any]]
    intent_confidence: float

    # Time parsing results
    parsed_times: Optional[Dict[str, Any]]
    source_time: Optional[str]
    target_time: Optional[str]

    # Calendar query results
    source_event: Optional[CalendarEvent]
    target_slot: Optional[TimeSlot]

    # Conflict detection
    conflicts: List[CalendarEvent]
    conflict_result: Optional[ConflictResult]

    # Action plan
    action_plan: Optional[Dict[str, Any]]

    # Execution results
    execution_results: List[Dict[str, Any]]
    errors: List[str]

    # Email notification
    email_sent: bool
    email_recipients: List[str]

    # Final response
    response: str

    # Control flow
    needs_user_confirmation: bool
    should_continue: bool