"""
Execution Engine Node

Executes the planned actions (calendar operations, email notifications)
"""

from typing import Dict, Any
from datetime import datetime
from models.agent_state import AgentState
from services.local_calendar import LocalCalendarService
from services.smtp_email import SMTPEmailService
from config import settings
from loguru import logger


def execution_engine_node(state: AgentState) -> Dict[str, Any]:
    """
    Execution engine node

    Args:
        state: Current agent state with action plan

    Returns:
        Updated state with execution results
    """
    logger.info("🚀 Starting execution engine...")

    action_plan = state.get("action_plan", {})
    action = action_plan.get("action", "")

    calendar_service = LocalCalendarService()
    email_service = SMTPEmailService()
    execution_results = []
    response = ""

    try:
        if action == "query_events":
            # Execute: Query events
            start_time = datetime.fromisoformat(action_plan["start_time"])
            end_time = datetime.fromisoformat(action_plan["end_time"])

            events = calendar_service.list_events(start_time, end_time)

            if events:
                event_list = "\n".join([
                    f"  • {e['title']} ({e['start_time'].strftime('%H:%M')}-{e['end_time'].strftime('%H:%M')})"
                    if isinstance(e['start_time'], datetime)
                    else f"  • {e['title']}"
                    for e in events
                ])
                response = f"📅 {action_plan['description']}:\n{event_list}"
            else:
                response = f"📅 {action_plan['description']}:\n  暂无安排"

            execution_results.append({
                "action": "query_events",
                "success": True,
                "events_count": len(events)
            })

        elif action == "reschedule_event":
            # Execute: Update event time
            event_id = action_plan["event_id"]
            new_start = datetime.fromisoformat(action_plan["new_start"])
            old_start_str = action_plan["current_start"]

            # Calculate new end time (keep same duration)
            if isinstance(old_start_str, str):
                old_start = datetime.fromisoformat(old_start_str)
                duration = timedelta(hours=1)  # Default
                # Try to get actual duration from original event
                original_event = calendar_service.get_event(event_id)
                if original_event:
                    orig_start = original_event["start_time"] if isinstance(original_event["start_time"], datetime) else datetime.fromisoformat(original_event["start_time"])
                    orig_end = original_event["end_time"] if isinstance(original_event["end_time"], datetime) else datetime.fromisoformat(original_event["end_time"])
                    duration = orig_end - orig_start

            new_end = new_start + duration

            success = calendar_service.update_event(event_id, {
                "start_time": new_start,
                "end_time": new_end
            })

            if success:
                execution_results.append({
                    "action": "update_event",
                    "success": True,
                    "event_id": event_id
                })

                # Send email notification if attendees exist
                attendees = action_plan.get("attendees", [])
                if attendees and settings.EMAIL_NOTIFICATION_ENABLED:
                    try:
                        email_sent = email_service.send_meeting_notification(
                            attendees=attendees,
                            event_title=action_plan.get("event_title", "会议"),
                            old_time=old_start_str,
                            new_time=new_start.isoformat()
                        )

                        execution_results.append({
                            "action": "send_notification",
                            "success": email_sent,
                            "recipients": attendees
                        })

                        response = f"✅ {action_plan['description']}\n📧 已通知 {len(attendees)} 位参会人"
                    except Exception as e:
                        logger.warning(f"Failed to send email: {e}")
                        response = f"✅ {action_plan['description']}\n⚠️ 邮件通知发送失败"
                else:
                    response = f"✅ {action_plan['description']}"
            else:
                response = f"❌ 更新事件失败"
                execution_results.append({
                    "action": "update_event",
                    "success": False,
                    "error": "Update failed"
                })

        elif action == "create_event":
            # Execute: Create new event
            event_data = {
                "title": action_plan["title"],
                "start_time": datetime.fromisoformat(action_plan["start_time"]),
                "end_time": datetime.fromisoformat(action_plan["end_time"]),
                "location": action_plan.get("location", ""),
                "attendees": action_plan.get("attendees", []),
                "organizer": settings.EMAIL_SENDER
            }

            event_id = calendar_service.create_event(event_data)

            execution_results.append({
                "action": "create_event",
                "success": True,
                "event_id": event_id
            })

            response = f"✅ 成功创建事件: {action_plan['title']}"

        elif action == "delete_event":
            # Execute: Delete event
            event_id = action_plan["event_id"]
            success = calendar_service.delete_event(event_id)

            if success:
                execution_results.append({
                    "action": "delete_event",
                    "success": True,
                    "event_id": event_id
                })
                response = f"✅ {action_plan['description']}"
            else:
                response = f"❌ 删除事件失败"
                execution_results.append({
                    "action": "delete_event",
                    "success": False
                })

        else:
            response = f"⚠️ 未知操作: {action}"

        logger.info(f"✅ Execution completed: {response}")

        return {
            "execution_results": execution_results,
            "response": response,
            "should_continue": False
        }

    except Exception as e:
        logger.error(f"❌ Execution failed: {e}")
        return {
            "execution_results": execution_results,
            "errors": state.get("errors", []) + [f"Execution error: {str(e)}"],
            "response": f"❌ 执行失败: {str(e)}",
            "should_continue": False
        }
