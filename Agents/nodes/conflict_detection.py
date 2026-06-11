"""
Conflict Detection Node

Checks for scheduling conflicts and suggests alternative times
"""

from typing import Dict, Any
from datetime import datetime, timedelta
from models.agent_state import AgentState
from models.calendar_event import ConflictResult, TimeSlot
from services.local_calendar import LocalCalendarService
from loguru import logger


def conflict_detection_node(state: AgentState) -> Dict[str, Any]:
    """
    Conflict detection node

    Args:
        state: Current agent state with action plan

    Returns:
        Updated state with conflict detection results
    """
    logger.info("⚠️ Starting conflict detection...")

    action_plan = state.get("action_plan", {})
    action = action_plan.get("action", "")

    calendar_service = LocalCalendarService()

    try:
        if action in ["reschedule_event", "create_event"]:
            # Extract target time from action plan
            target_time_str = action_plan.get("new_start") or action_plan.get("start_time")

            if not target_time_str:
                logger.warning("⚠️ No target time found in action plan")
                return {
                    "conflicts": [],
                    "conflict_result": ConflictResult(
                        has_conflict=False,
                        message="无目标时间，跳过冲突检测"
                    ),
                    "should_continue": True
                }

            target_time = datetime.fromisoformat(target_time_str)
            duration_hours = 1  # Default 1 hour
            end_time = target_time + timedelta(hours=duration_hours)

            # Check for conflicts
            event_id = action_plan.get("event_id")  # Exclude current event if rescheduling
            conflicts = calendar_service.check_conflicts(
                target_time,
                end_time,
                exclude_id=event_id
            )

            logger.info(f"🔍 Found {len(conflicts)} conflicts")

            if conflicts:
                # Has conflicts - find alternative slots
                suggested_slots = calendar_service.find_available_slots(
                    target_time.date(),
                    duration_minutes=60
                )

                conflict_result = ConflictResult(
                    has_conflict=True,
                    conflicting_events=conflicts,
                    suggested_slots=[
                        TimeSlot(
                            start=slot["start"],
                            end=slot["end"],
                            time_str=slot.get("time_str", "")
                        )
                        for slot in suggested_slots
                    ],
                    message=f"时间冲突！找到 {len(conflicts)} 个冲突事件，建议改用以下时间"
                )

                logger.warning(f"⚠️ Conflict detected: {conflict_result.message}")

                return {
                    "conflicts": conflicts,
                    "conflict_result": conflict_result,
                    "needs_user_confirmation": True,
                    "should_continue": False  # Need user to choose alternative
                }
            else:
                # No conflicts
                conflict_result = ConflictResult(
                    has_conflict=False,
                    message="时间可用，无冲突"
                )

                logger.info("✅ No conflicts detected")

                return {
                    "conflicts": [],
                    "conflict_result": conflict_result,
                    "should_continue": True
                }

        else:
            # For query/delete/update actions, skip conflict detection
            logger.info("ℹ️ Skipping conflict detection for this action")
            return {
                "conflicts": [],
                "conflict_result": ConflictResult(has_conflict=False),
                "should_continue": True
            }

    except Exception as e:
        logger.error(f"❌ Conflict detection failed: {e}")
        return {
            "conflicts": [],
            "conflict_result": ConflictResult(
                has_conflict=False,
                message=f"冲突检测失败: {str(e)}"
            ),
            "errors": state.get("errors", []) + [f"Conflict detection error: {str(e)}"],
            "should_continue": True  # Continue anyway, just log the error
        }
