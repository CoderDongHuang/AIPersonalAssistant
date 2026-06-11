"""
Local Calendar Service

Uses SQLite database to simulate Google Calendar API
No external dependencies required, works offline
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path
from loguru import logger


class LocalCalendarService:
    """Local calendar service using SQLite"""

    def __init__(self, db_path: str = "calendar.db"):
        """Initialize local calendar service"""
        self.db_path = Path(db_path)
        self._init_database()
        self._seed_sample_data()
        logger.info(f"LocalCalendarService initialized: {self.db_path}")

    def _init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                location TEXT DEFAULT '',
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP NOT NULL,
                attendees TEXT DEFAULT '',
                organizer TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        logger.debug("Database schema initialized")

    def _seed_sample_data(self):
        """Insert sample events for testing"""
        if self._has_events():
            logger.debug("Database already has events, skip seeding")
            return

        now = datetime.now()

        sample_events = [
            {
                'id': 'evt_001',
                'title': '团队周会',
                'description': '每周团队同步会议，讨论项目进度',
                'location': '会议室A',
                'start_time': (now + timedelta(days=2, hours=14)).isoformat(),
                'end_time': (now + timedelta(days=2, hours=15)).isoformat(),
                'attendees': '1218798773@qq.com,3064801244@qq.com,1368382140@qq.com',
                'organizer': '1218798773@qq.com'
            },
            {
                'id': 'evt_002',
                'title': '产品评审会议',
                'description': 'Q2产品功能评审',
                'location': '线上会议（腾讯会议）',
                'start_time': (now + timedelta(days=3, hours=10)).isoformat(),
                'end_time': (now + timedelta(days=3, hours=11, minutes=30)).isoformat(),
                'attendees': '1218798773@qq.com,3064801244@qq.com',
                'organizer': '1218798773@qq.com'
            },
            {
                'id': 'evt_003',
                'title': '技术分享',
                'description': 'LangGraph技术分享会',
                'location': '培训室B',
                'start_time': (now + timedelta(days=4, hours=15)).isoformat(),
                'end_time': (now + timedelta(days=4, hours=16, minutes=30)).isoformat(),
                'attendees': '1218798773@qq.com,3064801244@qq.com,1368382140@qq.com',
                'organizer': '1218798773@qq.com'
            }
        ]


        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for event in sample_events:
            cursor.execute('''
                INSERT OR IGNORE INTO events 
                (id, title, description, location, start_time, end_time, attendees, organizer)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event['id'],
                event['title'],
                event['description'],
                event['location'],
                event['start_time'],
                event['end_time'],
                event['attendees'],
                event['organizer']
            ))

        conn.commit()
        conn.close()

        logger.info(f"Seeded {len(sample_events)} sample events")

    def _has_events(self) -> bool:
        """Check if database has any events"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM events")
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    def list_events(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """
        Get events within time range

        Args:
            start_time: Start of time range
            end_time: End of time range

        Returns:
            List of event dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM events 
            WHERE start_time >= ? AND start_time <= ?
            ORDER BY start_time
        ''', (start_time.isoformat(), end_time.isoformat()))

        rows = cursor.fetchall()
        events = [self._row_to_dict(dict(row)) for row in rows]

        conn.close()
        logger.info(f"Retrieved {len(events)} events from {start_time} to {end_time}")
        return events

    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Get single event by ID

        Args:
            event_id: Event identifier

        Returns:
            Event dictionary or None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        row = cursor.fetchone()

        conn.close()

        if row:
            logger.info(f"Retrieved event: {event_id}")
            return self._row_to_dict(dict(row))
        else:
            logger.warning(f"Event not found: {event_id}")
            return None

    def update_event(self, event_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an event

        Args:
            event_id: Event identifier
            updates: Dictionary of fields to update

        Returns:
            True if successful, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Build dynamic UPDATE query
        set_clauses = []
        values = []

        allowed_fields = ['title', 'description', 'location', 'start_time', 'end_time']

        for key, value in updates.items():
            if key in allowed_fields:
                set_clauses.append(f"{key} = ?")
                if isinstance(value, datetime):
                    values.append(value.isoformat())
                else:
                    values.append(value)
            elif key == 'attendees' and isinstance(value, list):
                set_clauses.append("attendees = ?")
                values.append(','.join(value))

        if not set_clauses:
            logger.warning("No valid fields to update")
            conn.close()
            return False

        set_clauses.append("updated_at = ?")
        values.extend([datetime.now().isoformat(), event_id])

        query = f"UPDATE events SET {', '.join(set_clauses)} WHERE id = ?"
        cursor.execute(query, values)

        conn.commit()
        affected_rows = cursor.rowcount
        conn.close()

        if affected_rows > 0:
            logger.info(f"Event updated: {event_id}")
            return True
        else:
            logger.warning(f"Event not found: {event_id}")
            return False

    def create_event(self, event: Dict[str, Any]) -> str:
        """
        Create a new event

        Args:
            event: Event data dictionary

        Returns:
            Event ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        event_id = event.get('id', f"evt_{int(datetime.now().timestamp())}")

        attendees_str = ','.join(event.get('attendees', []))

        cursor.execute('''
            INSERT INTO events (id, title, description, location, 
                              start_time, end_time, attendees, organizer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event_id,
            event.get('title'),
            event.get('description', ''),
            event.get('location', ''),
            event['start_time'].isoformat() if isinstance(event['start_time'], datetime) else event['start_time'],
            event['end_time'].isoformat() if isinstance(event['end_time'], datetime) else event['end_time'],
            attendees_str,
            event.get('organizer', '')
        ))

        conn.commit()
        conn.close()

        logger.info(f"Event created: {event_id}")
        return event_id

    def delete_event(self, event_id: str) -> bool:
        """
        Delete an event

        Args:
            event_id: Event identifier

        Returns:
            True if successful, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))

        conn.commit()
        affected_rows = cursor.rowcount
        conn.close()

        if affected_rows > 0:
            logger.info(f"Event deleted: {event_id}")
            return True
        else:
            logger.warning(f"Event not found: {event_id}")
            return False

    def check_conflicts(self, start_time: datetime, end_time: datetime,
                       exclude_id: str = None) -> List[Dict[str, Any]]:
        """
        Check for scheduling conflicts

        Args:
            start_time: Start of proposed time slot
            end_time: End of proposed time slot
            exclude_id: Event ID to exclude (when updating)

        Returns:
            List of conflicting events
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if exclude_id:
            cursor.execute('''
                SELECT * FROM events 
                WHERE start_time < ? AND end_time > ?
                AND id != ?
                ORDER BY start_time
            ''', (end_time.isoformat(), start_time.isoformat(), exclude_id))
        else:
            cursor.execute('''
                SELECT * FROM events 
                WHERE start_time < ? AND end_time > ?
                ORDER BY start_time
            ''', (end_time.isoformat(), start_time.isoformat()))

        rows = cursor.fetchall()
        conflicts = [self._row_to_dict(dict(row)) for row in rows]

        conn.close()
        logger.info(f"Found {len(conflicts)} conflicts for time slot {start_time} - {end_time}")
        return conflicts

    def find_available_slots(self, date: datetime, duration_minutes: int = 60,
                            preferred_times: List[str] = None) -> List[Dict[str, datetime]]:
        """
        Find available time slots on a given date

        Args:
            date: Date to search
            duration_minutes: Required duration in minutes
            preferred_times: Preferred time slots like ['09:00', '14:00', '16:00']

        Returns:
            List of available time slots
        """
        if preferred_times is None:
            preferred_times = ['09:00', '10:00', '14:00', '15:00', '16:00']

        available_slots = []

        for time_str in preferred_times:
            hour, minute = map(int, time_str.split(':'))
            slot_start = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            slot_end = slot_start + timedelta(minutes=duration_minutes)

            conflicts = self.check_conflicts(slot_start, slot_end)

            if not conflicts:
                available_slots.append({
                    'start': slot_start,
                    'end': slot_end,
                    'time_str': time_str
                })

        logger.info(f"Found {len(available_slots)} available slots on {date.date()}")
        return available_slots

    def _row_to_dict(self, row_dict: Dict) -> Dict[str, Any]:
        """Convert database row to event dictionary"""
        event = row_dict.copy()

        # Parse attendees from string to list
        if event.get('attendees'):
            event['attendees'] = [a.strip() for a in event['attendees'].split(',') if a.strip()]
        else:
            event['attendees'] = []

        # Parse datetime strings
        if isinstance(event.get('start_time'), str):
            event['start_time'] = datetime.fromisoformat(event['start_time'])
        if isinstance(event.get('end_time'), str):
            event['end_time'] = datetime.fromisoformat(event['end_time'])

        return event


# Global instance
local_calendar = LocalCalendarService()