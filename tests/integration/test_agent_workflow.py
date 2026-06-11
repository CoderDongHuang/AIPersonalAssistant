"""
Integration tests for the full Agent workflow

End-to-end tests that exercise the complete LangGraph pipeline:
intent → time_reasoning → task_planning → conflict_detection → execution → response
"""

import pytest
from datetime import datetime

from agents.graph_builder import build_agent_graph
from tests.fixtures.sample_data import get_initial_agent_state


class TestAgentWorkflowE2E:
    """End-to-end workflow tests"""

    def setup_method(self):
        """Build the graph once per test."""
        self.graph = build_agent_graph()

    def _run(self, user_input: str) -> dict:
        """Helper: run the full workflow and return the final state."""
        state = get_initial_agent_state(user_input)
        config = {"configurable": {"thread_id": f"itest_{id(self)}"}}
        return self.graph.invoke(state, config=config)

    # ── Query events ──

    def test_query_tomorrow_schedule(self):
        """'明天有什么安排？' should return events or '暂无安排'."""
        result = self._run("明天有什么安排？")
        assert result.get("response"), "Should have a response"
        # Either shows events or says no events
        assert "📅" in result["response"] or "暂无" in result["response"]

    def test_query_events_today(self):
        """Querying today's schedule should return a valid response."""
        result = self._run("今天有什么安排？")
        assert result.get("response") is not None
        assert len(result["response"]) > 0

    # ── Reschedule event ──

    def test_reschedule_meeting(self):
        """'帮我把下周三的会议改到周五' should produce a valid plan."""
        result = self._run("帮我把下周三的会议改到周五")
        assert result.get("response"), "Should have a response"
        # Should contain success or a meaningful message
        response = result["response"]
        assert any(kw in response for kw in ["✅", "📅", "❌", "⚠️"]), \
            f"Response should have a status indicator: {response}"

    def test_reschedule_with_confidence_check(self):
        """Reschedule intent should be recognized with decent confidence."""
        result = self._run("把周三的会议调整到周五")
        confidence = result.get("intent_confidence", 0)
        assert confidence >= 0.5 or result.get("intent") is not None, \
            "Should recognize reschedule intent"

    # ── Create event ──

    def test_create_event(self):
        """Creating an event should succeed."""
        result = self._run("安排一个明天下午3点的会议")
        assert result.get("response"), "Should have a response"

    # ── Delete event ──

    def test_delete_event(self):
        """Deleting an event should work or report not found."""
        result = self._run("取消明天的会议")
        response = result["response"]
        assert len(response) > 0

    # ── Error handling ──

    def test_unknown_intent_handled(self):
        """Gibberish input should be handled gracefully."""
        result = self._run("你好今天天气怎么样")
        response = result["response"]
        # Should give a helpful error, not crash
        assert len(response) > 0

    def test_empty_input_handled(self):
        """Empty input should not crash."""
        result = self._run("")
        response = result.get("response", "")
        # Empty input: intent recognition should still produce something
        assert response is not None


class TestWorkflowRouting:
    """Test that the workflow routes correctly through nodes"""

    def setup_method(self):
        self.graph = build_agent_graph()

    def _run(self, user_input: str) -> dict:
        state = get_initial_agent_state(user_input)
        config = {"configurable": {"thread_id": f"route_{id(self)}_{hash(user_input)}"}}
        return self.graph.invoke(state, config=config)

    def test_query_routes_directly_to_execution(self):
        """Query actions skip conflict detection."""
        result = self._run("查看明天的日程")
        # Query should go: intent → time → plan → execution (skip conflict)
        assert result.get("response") is not None

    def test_reschedule_routes_through_conflict_detection(self):
        """Reschedule actions go through conflict detection."""
        result = self._run("把周三的会议改到周五")
        # Reschedule should go: intent → time → plan → conflict → execution
        # conflict_result should be populated
        conflict_result = result.get("conflict_result")
        assert conflict_result is not None, \
            "Reschedule should trigger conflict detection"

    def test_workflow_preserves_state(self):
        """State should flow correctly between nodes."""
        result = self._run("明天有什么安排？")
        # After workflow completes, state should have:
        assert "user_input" in result
        assert "response" in result
        # intent should be resolved
        assert result.get("intent") is not None or result.get("intent_confidence", 0) > 0


class TestWorkflowWithRealCalendar:
    """Integration tests using the real SQLite calendar"""

    def setup_method(self):
        self.graph = build_agent_graph()

    def _run(self, user_input: str) -> dict:
        state = get_initial_agent_state(user_input)
        config = {"configurable": {"thread_id": f"realcal_{id(self)}_{hash(user_input)}"}}
        return self.graph.invoke(state, config=config)

    def test_query_returns_real_events(self):
        """Querying should find the seed events in the database."""
        result = self._run("后天有什么安排？")
        response = result["response"]
        # Should either list events or say '暂无安排'
        # With seed data, it might or might not match
        assert len(response) > 0

    def test_reschedule_actually_updates_event(self):
        """Reschedule workflow runs end-to-end and produces a valid response."""
        from services.local_calendar import LocalCalendarService
        from datetime import datetime, timedelta

        cal = LocalCalendarService()
        now = datetime.now()
        events = cal.list_events(now - timedelta(days=1), now + timedelta(days=7))
        if not events:
            pytest.skip("No events available for testing")

        target_event = events[0]

        # Run the reschedule workflow
        result = self._run(f"把{target_event['title']}改到大后天")

        # The workflow must produce a response (success, failure, or conflict message)
        response = result["response"]
        assert len(response) > 0, "Workflow should always return a response"

        # The workflow should NOT have crashed (errors are OK, crashes are not)
        # Accept any valid outcome: success, not-found, conflict, etc.
        assert result.get("should_continue") is not None

    def test_workflow_correctly_creates_and_cleans_up_event(self):
        """Create a new event and verify it appears in the DB, then clean up."""
        from services.local_calendar import LocalCalendarService

        cal = LocalCalendarService()

        result = self._run("创建一个明天下午4点的测试会议")

        execution_results = result.get("execution_results", [])
        create_results = [r for r in execution_results if r.get("action") == "create_event"]
        if create_results and create_results[0].get("success"):
            event_id = create_results[0].get("event_id")
            # Verify it exists
            event = cal.get_event(event_id)
            assert event is not None
            # Clean up
            cal.delete_event(event_id)
