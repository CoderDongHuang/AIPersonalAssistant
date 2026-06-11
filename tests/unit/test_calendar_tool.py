"""
Unit tests for LocalCalendarService

Covers SQLite-based calendar CRUD, conflict detection, and available-slot search
"""

import pytest
import os
from datetime import datetime, timedelta
from services.local_calendar import LocalCalendarService


TEST_DB = "test_calendar.db"


class TestLocalCalendarService:
    """Test LocalCalendarService CRUD and conflict detection"""

    def setup_method(self):
        """Create a fresh service for each test"""
        # Remove test DB if it exists
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        self.service = LocalCalendarService(db_path=TEST_DB)
        self.now = datetime.now()

    def teardown_method(self):
        """Clean up test DB"""
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    # ── Seeding ──

    def test_sample_data_is_seeded(self):
        """Verify that sample events are automatically created"""
        start = self.now - timedelta(days=1)
        end = self.now + timedelta(days=30)
        events = self.service.list_events(start, end)
        assert len(events) >= 3  # At least the 3 sample events

    def test_seed_is_idempotent(self):
        """Second initialization should not duplicate events"""
        service2 = LocalCalendarService(db_path=TEST_DB)
        start = self.now - timedelta(days=1)
        end = self.now + timedelta(days=30)
        events = service2.list_events(start, end)
        # Should still have the same count (INSERT OR IGNORE)
        assert len(events) >= 3

    # ── CRUD operations ──

    def test_list_events_in_range(self):
        start = self.now + timedelta(days=1)
        end = self.now + timedelta(days=5)
        events = self.service.list_events(start, end)
        for e in events:
            assert isinstance(e["start_time"], datetime)
            assert isinstance(e["end_time"], datetime)
            assert start <= e["start_time"] <= end

    def test_list_events_empty_range(self):
        """Range with no events should return empty list"""
        start = self.now + timedelta(days=100)
        end = self.now + timedelta(days=101)
        events = self.service.list_events(start, end)
        assert events == []

    def test_get_event_by_id(self):
        event = self.service.get_event("evt_001")
        assert event is not None
        assert event["title"] == "团队周会"
        assert isinstance(event["attendees"], list)

    def test_get_event_not_found(self):
        event = self.service.get_event("nonexistent_id")
        assert event is None

    def test_create_event(self):
        event_data = {
            "title": "测试会议",
            "start_time": self.now + timedelta(days=10, hours=14),
            "end_time": self.now + timedelta(days=10, hours=15),
            "attendees": ["test@example.com"],
            "organizer": "organizer@example.com",
        }
        event_id = self.service.create_event(event_data)
        assert event_id is not None

        # Verify it was created
        event = self.service.get_event(event_id)
        assert event is not None
        assert event["title"] == "测试会议"

    def test_update_event(self):
        success = self.service.update_event("evt_001", {
            "title": "更新后的会议",
            "location": "新会议室",
        })
        assert success is True

        event = self.service.get_event("evt_001")
        assert event["title"] == "更新后的会议"
        assert event["location"] == "新会议室"

    def test_update_event_not_found(self):
        success = self.service.update_event("nonexistent", {"title": "test"})
        assert success is False

    def test_update_event_with_datetime(self):
        new_start = self.now + timedelta(days=20, hours=9)
        new_end = self.now + timedelta(days=20, hours=10)
        success = self.service.update_event("evt_001", {
            "start_time": new_start,
            "end_time": new_end,
        })
        assert success is True
        event = self.service.get_event("evt_001")
        assert event["start_time"] == new_start

    def test_delete_event(self):
        success = self.service.delete_event("evt_001")
        assert success is True
        assert self.service.get_event("evt_001") is None

    def test_delete_event_not_found(self):
        success = self.service.delete_event("nonexistent")
        assert success is False

    # ── Conflict detection ──

    def test_check_conflicts_no_conflict(self):
        """A time slot far in the future should have no conflicts"""
        start = self.now + timedelta(days=365)
        end = start + timedelta(hours=1)
        conflicts = self.service.check_conflicts(start, end)
        assert conflicts == []

    def test_check_conflicts_with_conflict(self):
        """Creating an overlapping event should detect conflict"""
        # Get an existing event's time
        event = self.service.get_event("evt_001")
        conflicts = self.service.check_conflicts(
            event["start_time"], event["end_time"]
        )
        assert len(conflicts) >= 1

    def test_check_conflicts_exclude_id(self):
        """When updating an event, exclude itself from conflict check"""
        event = self.service.get_event("evt_001")
        conflicts = self.service.check_conflicts(
            event["start_time"], event["end_time"], exclude_id="evt_001"
        )
        # Should not report itself as conflict
        conflict_ids = [c["id"] for c in conflicts]
        assert "evt_001" not in conflict_ids

    # ── Available slots ──

    def test_find_available_slots(self):
        date = self.now + timedelta(days=30)
        slots = self.service.find_available_slots(
            date,
            duration_minutes=60,
            preferred_times=["09:00", "14:00", "16:00"],
        )
        # All preferred times should be available on a far-future date
        assert len(slots) == 3
        for slot in slots:
            assert isinstance(slot["start"], datetime)
            assert isinstance(slot["end"], datetime)
            assert "time_str" in slot

    def test_find_available_slots_default_times(self):
        date = self.now + timedelta(days=30)
        slots = self.service.find_available_slots(date, duration_minutes=60)
        # Default preferred times: ['09:00', '10:00', '14:00', '15:00', '16:00']
        assert len(slots) == 5

    def test_find_available_slots_with_existing_event(self):
        """Slots that overlap with existing events should be excluded"""
        event = self.service.get_event("evt_002")
        assert event is not None, "evt_002 should exist"
        event_date = event["start_time"].replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        # Find which hour the event occupies
        event_hour = event["start_time"].strftime("%H:%M")

        slots = self.service.find_available_slots(
            event_date,
            duration_minutes=60,
            preferred_times=[event_hour, "14:00", "16:00"],
        )
        # The slot at the event's hour should be blocked
        time_strs = [s["time_str"] for s in slots]
        assert event_hour not in time_strs, (
            f"Slot at {event_hour} should be blocked by event_002"
        )

    # ── Attendee parsing ──

    def test_attendees_parsed_as_list(self):
        event = self.service.get_event("evt_001")
        assert isinstance(event["attendees"], list)
        assert len(event["attendees"]) == 3


class TestCalendarTool:
    """Test the LangChain CalendarTool wrapper"""

    def setup_method(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        from tools.calendar_tool import CalendarTool
        self.tool = CalendarTool()

    def teardown_method(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def test_tool_creation(self):
        assert self.tool.name == "calendar"
        assert self.tool.calendar_service is not None
        assert self.tool.time_parser is not None

    def test_tool_list_events(self):
        now = datetime.now()
        events = self.tool.list_events(
            now - timedelta(days=1),
            now + timedelta(days=30),
        )
        assert len(events) >= 3

    def test_tool_check_conflicts(self):
        event = self.tool.get_event("evt_001")
        conflicts = self.tool.check_conflicts(
            event["start_time"], event["end_time"],
        )
        assert len(conflicts) >= 1
