"""
Time Reasoning Node

Parses natural language time expressions into concrete datetime objects
"""

from typing import Dict, Any
from datetime import datetime, timedelta
from models.agent_state import AgentState
from tools.time_parser import TimeParser
from loguru import logger


def time_reasoning_node(state: AgentState) -> Dict[str, Any]:
    """
    Time reasoning node

    Args:
        state: Current agent state with intent

    Returns:
        Updated state with parsed time information
    """
    logger.info("⏰ Starting time reasoning...")

    intent = state.get("intent", {})
    action = intent.get("action", "")

    logger.debug(f"📋 Intent data: {intent}")

    time_parser = TimeParser()
    parsed_times = {}
    source_time = None
    target_time = None

    try:
        # Parse source time (for reschedule operations)
        if "source_time" in intent and intent["source_time"]:
            source_time_str = intent["source_time"]
            logger.info(f"🔍 Parsing source time: '{source_time_str}'")
            source_time = time_parser.parse_time_expression(source_time_str)
            if source_time:
                parsed_times["source_time"] = source_time.isoformat()
                logger.info(f"✅ Parsed source time: {source_time_str} -> {source_time}")
            else:
                logger.warning(f"⚠️ Failed to parse source time: {source_time_str}")

        # Parse target time (for reschedule/create operations)
        if "target_time" in intent and intent["target_time"]:
            target_time_str = intent["target_time"]
            logger.info(f"🔍 Parsing target time: '{target_time_str}'")
            target_time = time_parser.parse_time_expression(target_time_str)
            if target_time:
                parsed_times["target_time"] = target_time.isoformat()
                logger.info(f"✅ Parsed target time: {target_time_str} -> {target_time}")
            else:
                logger.warning(f"⚠️ Failed to parse target time: {target_time_str}")

        # Parse date for query operations
        if "date" in intent and intent["date"]:
            date_str = intent["date"]
            parsed_date = time_parser.parse_time_expression(date_str)
            if parsed_date:
                parsed_times["date"] = parsed_date.isoformat()
                logger.info(f"✅ Parsed date: {date_str} -> {parsed_date}")

        # If no specific time parsing succeeded, try to extract from user_input
        if not source_time and not target_time:
            user_input = state.get("user_input", "")
            logger.info(f"🔍 Trying fallback parsing from user input: '{user_input}'")
            fallback_time = time_parser.parse_time_expression(user_input)
            if fallback_time:
                parsed_times["fallback_time"] = fallback_time.isoformat()
                logger.info(f"✅ Parsed fallback time from input: {fallback_time}")

        # Prepare return values
        updates = {
            "parsed_times": parsed_times,
            "should_continue": len(parsed_times) > 0
        }

        # Set source_time and target_time for routing logic
        if source_time:
            updates["source_time"] = source_time.isoformat()
        if target_time:
            updates["target_time"] = target_time.isoformat()

        if not updates["should_continue"]:
            updates["errors"] = state.get("errors", []) + ["无法解析时间表达式"]
            logger.warning("⚠️ No time expressions could be parsed")

        return updates

    except Exception as e:
        logger.error(f"❌ Time reasoning failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            "parsed_times": {},
            "source_time": None,
            "target_time": None,
            "errors": state.get("errors", []) + [f"Time reasoning error: {str(e)}"],
            "should_continue": False
        }

