"""
Unit tests for LangGraph agent nodes

Tests intent recognition (rule-based fallback), time reasoning,
task planning, conflict detection, and error handler nodes
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from models.agent_state import AgentState
from models.calendar_event import ConflictResult, TimeSlot
from tests.fixtures.sample_data import (
    NOW, SAMPLE_EVENTS, INTENT_TEST_CASES,
    get_initial_agent_state,
)


class TestIntentRecognition:
    """Test the intent recognition node (rule-based fallback)"""

    def test_recognize_query_intent(self):
        from agents.nodes.intent_recognition import _recognize_with_rules

        result = _recognize_with_rules("明天有什么安排？")
        assert result["action"] == "query_events"

    def test_recognize_reschedule_intent(self):
        from agents.nodes.intent_recognition import _recognize_with_rules

        result = _recognize_with_rules("把下周三的会议改到周五")
        assert result["action"] == "reschedule_event"

    def test_recognize_create_intent(self):
        from agents.nodes.intent_recognition import _recognize_with_rules

        result = _recognize_with_rules("创建一个新会议")
        assert result["action"] == "create_event"

    def test_recognize_delete_intent(self):
        from agents.nodes.intent_recognition import _recognize_with_rules

        result = _recognize_with_rules("取消明天的会议")
        assert result["action"] == "delete_event"

    def test_recognize_unknown_intent(self):
        from agents.nodes.intent_recognition import _recognize_with_rules

        result = _recognize_with_rules("你好")
        assert result["action"] == "unknown"
        assert result["confidence"] < 0.5

    @pytest.mark.parametrize("case", INTENT_TEST_CASES)
    def test_intent_recognition_cases(self, case):
        from agents.nodes.intent_recognition import _recognize_with_rules

        result = _recognize_with_rules(case["input"])
        assert result["action"] == case["expected_action"], \
            f"Failed for: {case['input']}"

    def test_intent_node_without_llm(self):
        """Full node should work without LLM (rule-based fallback)"""
        from agents.nodes.intent_recognition import intent_recognition_node
        from config import settings

        # Temporarily clear API key to force rule-based path
        original_key = settings.OPENAI_API_KEY
        settings.OPENAI_API_KEY = ""

        try:
            state = get_initial_agent_state("帮我把下周三的会议改到周五")
            result = intent_recognition_node(state)

            assert result["intent"] is not None
            assert result["intent_confidence"] >= 0.5
            # The intent dict (from parameters) should contain action
            assert result["intent"].get("action") == "reschedule_event"
        finally:
            settings.OPENAI_API_KEY = original_key


class TestTimeReasoning:
    """Test the time reasoning node"""

    def test_parse_source_and_target_times(self):
        from agents.nodes.time_reasoning import time_reasoning_node

        state = get_initial_agent_state("帮我把下周三下午的会议改到周五")
        state["intent"] = {
            "action": "reschedule_event",
            "event_name": "会议",
            "source_time": "下周三下午",
            "target_time": "周五",
        }

        result = time_reasoning_node(state)
        assert result["should_continue"] is True
        assert result.get("source_time") is not None
        assert result.get("target_time") is not None

    def test_parse_query_date(self):
        from agents.nodes.time_reasoning import time_reasoning_node

        state = get_initial_agent_state("明天有什么安排？")
        state["intent"] = {
            "action": "query_events",
            "date": "明天",
        }

        result = time_reasoning_node(state)
        assert result["should_continue"] is True
        assert "date" in result.get("parsed_times", {})

    def test_fallback_to_user_input(self):
        from agents.nodes.time_reasoning import time_reasoning_node

        state = get_initial_agent_state("明天下午开会")
        state["intent"] = {
            "action": "create_event",
            "event_name": "开会",
        }

        result = time_reasoning_node(state)
        assert "fallback_time" in result.get("parsed_times", {}) or result["should_continue"]


class TestTaskPlanning:
    """Test the task planning node"""

    def test_plan_query_events(self):
        from agents.nodes.task_planning import task_planning_node

        tomorrow = (NOW + timedelta(days=1)).isoformat()
        state = get_initial_agent_state("明天有什么安排？")
        state["intent"] = {"action": "query_events"}
        state["parsed_times"] = {"date": tomorrow}

        result = task_planning_node(state)
        assert result["should_continue"] is True
        assert result["action_plan"]["action"] == "query_events"

    def test_plan_reschedule_with_sample_data(self):
        from agents.nodes.task_planning import task_planning_node

        source_time = (NOW + timedelta(days=2, hours=14)).isoformat()
        target_time = (NOW + timedelta(days=5, hours=14)).isoformat()

        state = get_initial_agent_state("把周三的会议改到周五")
        state["intent"] = {"action": "reschedule_event"}
        state["parsed_times"] = {
            "source_time": source_time,
            "target_time": target_time,
        }
        state["source_time"] = source_time
        state["target_time"] = target_time

        result = task_planning_node(state)
        assert result["should_continue"] is True
        assert result["action_plan"]["action"] == "reschedule_event"
        assert "event_id" in result["action_plan"]

    def test_plan_reschedule_missing_times_uses_sample_data(self):
        """When times are missing, should fall back to sample data"""
        from agents.nodes.task_planning import task_planning_node

        state = get_initial_agent_state("重新安排会议")
        state["intent"] = {"action": "reschedule_event"}
        state["parsed_times"] = {}

        result = task_planning_node(state)
        # Should still succeed with sample event data
        assert result["should_continue"] is True
        assert result["action_plan"]["action"] == "reschedule_event"
        assert "event_id" in result["action_plan"]

    def test_plan_unknown_action(self):
        from agents.nodes.task_planning import task_planning_node

        state = get_initial_agent_state("do something weird")
        state["intent"] = {"action": "unknown_action"}

        result = task_planning_node(state)
        assert result["should_continue"] is False
        assert len(result.get("errors", [])) > 0


class TestConflictDetection:
    """Test the conflict detection node"""

    def test_skip_for_query_action(self):
        from agents.nodes.conflict_detection import conflict_detection_node

        state = get_initial_agent_state("query")
        state["action_plan"] = {"action": "query_events"}

        result = conflict_detection_node(state)
        assert result["should_continue"] is True
        assert result["conflict_result"].has_conflict is False

    def test_detect_conflict_for_existing_event(self):
        from agents.nodes.conflict_detection import conflict_detection_node
        from services.local_calendar import LocalCalendarService
        from datetime import datetime, timedelta

        # Find any existing events (DB may have been modified by integration tests)
        cal = LocalCalendarService()
        now = datetime.now()
        events = cal.list_events(now - timedelta(days=1), now + timedelta(days=30))

        if len(events) < 2:
            pytest.skip("Need at least 2 events for conflict detection test")

        # Use the first event's time to create a conflict for the second event
        event_a = events[0]
        event_b = events[1]
        event_start = event_a["start_time"].isoformat()

        state = get_initial_agent_state("reschedule")
        state["action_plan"] = {
            "action": "reschedule_event",
            "event_id": event_b["id"],
            "new_start": event_start,
        }

        result = conflict_detection_node(state)
        # event_a is at the same time, so there should be a conflict
        assert result["conflict_result"].has_conflict is True
        assert len(result["conflicts"]) >= 1


class TestErrorHandler:
    """Test the error handler node"""

    def test_intent_failure_message(self):
        from agents.nodes.error_handler import error_handler_node

        state = get_initial_agent_state("random text")
        state["intent"] = None
        state["intent_confidence"] = 0.0

        result = error_handler_node(state)
        assert "没有理解" in result["response"]

    def test_time_parsing_failure_message(self):
        from agents.nodes.error_handler import error_handler_node

        state = get_initial_agent_state("test")
        state["intent"] = {"action": "query_events"}
        state["intent_confidence"] = 0.8
        state["parsed_times"] = None

        result = error_handler_node(state)
        assert "无法解析时间" in result["response"]

    def test_general_error_message(self):
        from agents.nodes.error_handler import error_handler_node

        state = get_initial_agent_state("test")
        state["intent"] = {"action": "query_events"}
        state["intent_confidence"] = 0.8
        state["parsed_times"] = {"date": "..."}
        state["errors"] = ["API timeout", "Connection refused"]

        result = error_handler_node(state)
        assert "API timeout" in result["response"]

    def test_conflict_response_with_suggestions(self):
        from agents.nodes.error_handler import error_handler_node
        from models.calendar_event import ConflictResult, TimeSlot, CalendarEvent

        slot = TimeSlot(
            start=NOW + timedelta(days=5, hours=15),
            end=NOW + timedelta(days=5, hours=16),
            time_str="15:00",
        )
        conflict_event = CalendarEvent(
            id="evt_conflict",
            title="已有会议",
            start_time=NOW + timedelta(days=5, hours=14),
            end_time=NOW + timedelta(days=5, hours=15),
            attendees=["test@example.com"],
        )
        conflict = ConflictResult(
            has_conflict=True,
            conflicting_events=[conflict_event],
            suggested_slots=[slot],
            message="时间冲突！",
        )

        state = get_initial_agent_state("reschedule")
        state["conflict_result"] = conflict
        state["needs_user_confirmation"] = True

        result = error_handler_node(state)
        assert "冲突" in result["response"]
        assert "15:00" in result["response"]
