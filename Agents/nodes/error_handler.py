"""
Error Handler Node

Handles errors and generates user-friendly error messages
"""

from typing import Dict, Any
from models.agent_state import AgentState
from loguru import logger


def error_handler_node(state: AgentState) -> Dict[str, Any]:
    """
    Error handler node

    Args:
        state: Current agent state with errors

    Returns:
        Updated state with error response
    """
    logger.info("🛑 Handling errors...")

    errors = state.get("errors", [])
    conflict_result = state.get("conflict_result")
    needs_confirmation = state.get("needs_user_confirmation", False)

    response = ""

    try:
        # Case 1: Time conflict - suggest alternatives
        if needs_confirmation and conflict_result and conflict_result.has_conflict:
            response = generate_conflict_response(conflict_result)

        # Case 2: Intent recognition failed
        elif not state.get("intent") or state.get("intent_confidence", 0) < 0.5:
            response = (
                "❌ 抱歉，我没有理解您的指令。\n\n"
                "您可以这样说：\n"
                "  • '明天有什么安排？'\n"
                "  • '把下周三的会议改到周五'\n"
                "  • '取消明天的会议'"
            )

        # Case 3: Time parsing failed
        elif not state.get("parsed_times"):
            response = (
                "❌ 无法解析时间表达式。\n\n"
                "请尝试更明确的时间描述，例如：\n"
                "  • '下周三下午'\n"
                "  • '明天上午10点'\n"
                "  • '后天'"
            )

        # Case 4: General errors
        elif errors:
            error_messages = "\n".join([f"  • {err}" for err in errors[-3:]])  # Show last 3 errors
            response = f"❌ 处理过程中遇到错误：\n{error_messages}"

        else:
            response = "❌ 未知错误，请稍后重试"

        logger.info(f"✅ Error response generated")

        return {
            "response": response,
            "should_continue": False
        }

    except Exception as e:
        logger.error(f"❌ Error handler failed: {e}")
        return {
            "response": "❌ 系统错误，请稍后重试",
            "should_continue": False
        }


def generate_conflict_response(conflict_result) -> str:
    """Generate user-friendly conflict resolution message"""

    response = f"⚠️ {conflict_result.message}\n\n"

    # Show conflicting events
    if conflict_result.conflicting_events:
        response += "📅 冲突的事件：\n"
        for event in conflict_result.conflicting_events[:3]:  # Show max 3
            title = event.get("title", "未命名事件")
            start = event.get("start_time", "")
            if hasattr(start, "strftime"):
                start_str = start.strftime("%H:%M")
            else:
                start_str = str(start)
            response += f"  • {title} ({start_str})\n"
        response += "\n"

    # Show suggested alternative slots
    if conflict_result.suggested_slots:
        response += "💡 建议的可用时间：\n"
        for slot in conflict_result.suggested_slots[:5]:  # Show max 5
            time_str = slot.time_str or slot.start.strftime("%H:%M") if hasattr(slot.start, "strftime") else ""
            response += f"  • {time_str}\n"
        response += "\n请告诉我您想改用哪个时间？"
    else:
        response += "抱歉，当天没有找到合适的空闲时段。建议您：\n"
        response += "  • 选择其他日期\n"
        response += "  • 缩短会议时长\n"
        response += "  • 与参会人协商"

    return response
