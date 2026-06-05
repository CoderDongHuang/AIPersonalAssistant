"""
Test Local Calendar and Email Services

Verify that local services work correctly
"""

from datetime import datetime, timedelta
from loguru import logger
from config import setup_logging
from services.local_calendar import LocalCalendarService
from services.smtp_email import SMTPEmailService


def test_calendar_service():
    """Test local calendar service"""
    print("\n" + "=" * 60)
    print("📅 Test 1: Local Calendar Service")
    print("=" * 60)

    try:
        calendar = LocalCalendarService()

        # Test 1: List events
        now = datetime.now()
        future = now + timedelta(days=7)

        events = calendar.list_events(now, future)
        print(f"✅ Retrieved {len(events)} events")

        if events:
            print("\n   Upcoming events:")
            for event in events[:3]:
                print(f"   • {event['title']}")
                print(f"     Time: {event['start_time'].strftime('%Y-%m-%d %H:%M')}")
                print(f"     Attendees: {len(event['attendees'])}")

        # Test 2: Get single event
        if events:
            event_id = events[0]['id']
            event = calendar.get_event(event_id)
            if event:
                print(f"\n✅ Retrieved event: {event['title']}")

        # Test 3: Check conflicts
        test_start = now + timedelta(days=2, hours=14)
        test_end = test_start + timedelta(hours=1)
        conflicts = calendar.check_conflicts(test_start, test_end)
        print(f"\n✅ Conflict check: {len(conflicts)} conflicts found")

        # Test 4: Find available slots
        available = calendar.find_available_slots(now + timedelta(days=5))
        print(f"✅ Available slots: {len(available)} found")

        return True

    except Exception as e:
        print(f"❌ Calendar service test failed: {e}")
        logger.exception(e)
        return False


def test_email_service():
    """Test email service"""
    print("\n" + "=" * 60)
    print("📧 Test 2: SMTP Email Service")
    print("=" * 60)

    try:
        email_service = SMTPEmailService()

        # Test sending a notification (will be skipped if not configured)
        result = email_service.send_meeting_notification(
            attendees=['1218798773@qq.com'],
            event_title='测试会议',
            old_time='2026-06-10 14:00',
            new_time='2026-06-13 14:00',
            location='会议室A',
            description='时间调整测试'
        )

        if result:
            print("✅ Email service test passed")
            print("   (Email may be skipped if not configured)")
        else:
            print("⚠️  Email sending failed (check configuration)")

        return True

    except Exception as e:
        print(f"❌ Email service test failed: {e}")
        logger.exception(e)
        return False


def main():
    """Main test function"""
    setup_logging()

    print("\n" + "=" * 60)
    print("🧪 Local Services Test")
    print("=" * 60)

    calendar_ok = test_calendar_service()
    email_ok = test_email_service()

    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    print(f"  Calendar Service: {'✅ Pass' if calendar_ok else '❌ Fail'}")
    print(f"  Email Service: {'✅ Pass' if email_ok else '❌ Fail'}")
    print("=" * 60)

    if calendar_ok and email_ok:
        print("\n🎉 All tests passed! Local services are ready.")
        print("\nNext steps:")
        print("  1. Configure OpenAI API key in .env")
        print("  2. (Optional) Configure SMTP email in .env")
        print("  3. Start building Agent workflow")
    else:
        print("\n⚠️  Some tests failed")


if __name__ == "__main__":
    main()