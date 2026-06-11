"""
LangGraph State Graph Builder

Builds the complete agent workflow for the Personal AI Assistant
"""

from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from models.agent_state import AgentState
from agents.nodes.intent_recognition import intent_recognition_node
from agents.nodes.time_reasoning import time_reasoning_node
from agents.nodes.task_planning import task_planning_node
from agents.nodes.conflict_detection import conflict_detection_node
from agents.nodes.execution_engine import execution_engine_node
from agents.nodes.error_handler import error_handler_node
from loguru import logger


def should_continue(state: AgentState) -> Literal["time_reasoning", "error_handler"]:
    """Route from intent_recognition to time_reasoning or error_handler"""
    # Lower the threshold to 0.5 for rule-based recognition
    if state.get("intent") and state.get("intent_confidence", 0) >= 0.5:
        return "time_reasoning"
    else:
        return "error_handler"



def should_plan_or_error(state: AgentState) -> Literal["task_planning", "error_handler"]:
    """Route from time_reasoning to task_planning or error_handler"""
    # Route to task_planning if any time was successfully parsed
    if state.get("parsed_times") and len(state.get("parsed_times", {})) > 0:
        return "task_planning"
    else:
        return "error_handler"


def should_check_conflicts(state: AgentState) -> Literal["conflict_detection", "execution_engine", "error_handler"]:
    """Route from task_planning — check conflicts, go to execution, or handle error"""
    action_plan = state.get("action_plan")

    # If task planning failed, route to error handler
    if not action_plan:
        return "error_handler"

    action = action_plan.get("action", "")

    if action in ["reschedule_event", "create_event"]:
        return "conflict_detection"
    else:
        return "execution_engine"


def should_execute_or_suggest(state: AgentState) -> Literal["execution_engine", "error_handler"]:
    """Route from conflict_detection based on conflict status"""
    conflict_result = state.get("conflict_result")

    if conflict_result and hasattr(conflict_result, 'has_conflict') and conflict_result.has_conflict:
        # Has conflicts - need user confirmation
        return "error_handler"
    else:
        # No conflicts - proceed with execution
        return "execution_engine"


def build_agent_graph():
    """
    Build the complete LangGraph workflow

    Workflow:
    START -> intent_recognition -> time_reasoning -> task_planning
              -> conflict_detection (conditional) -> execution_engine -> END

    Error paths route to error_handler -> END
    """

    logger.info("Building LangGraph workflow...")

    # Initialize the graph builder with AgentState
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("intent_recognition", intent_recognition_node)
    workflow.add_node("time_reasoning", time_reasoning_node)
    workflow.add_node("task_planning", task_planning_node)
    workflow.add_node("conflict_detection", conflict_detection_node)
    workflow.add_node("execution_engine", execution_engine_node)
    workflow.add_node("error_handler", error_handler_node)

    # Set entry point
    workflow.set_entry_point("intent_recognition")

    # Add edges with conditional routing
    workflow.add_conditional_edges(
        source="intent_recognition",
        path=should_continue,
        path_map={
            "time_reasoning": "time_reasoning",
            "error_handler": "error_handler"
        }
    )

    workflow.add_conditional_edges(
        source="time_reasoning",
        path=should_plan_or_error,
        path_map={
            "task_planning": "task_planning",
            "error_handler": "error_handler"
        }
    )

    workflow.add_conditional_edges(
        source="task_planning",
        path=should_check_conflicts,
        path_map={
            "conflict_detection": "conflict_detection",
            "execution_engine": "execution_engine",
            "error_handler": "error_handler",
        }
    )

    workflow.add_conditional_edges(
        source="conflict_detection",
        path=should_execute_or_suggest,
        path_map={
            "execution_engine": "execution_engine",
            "error_handler": "error_handler"
        }
    )

    # Final nodes always go to END
    workflow.add_edge("execution_engine", END)
    workflow.add_edge("error_handler", END)

    # Add memory for checkpointing (development mode)
    checkpointer = MemorySaver()

    # Compile the graph
    graph = workflow.compile(checkpointer=checkpointer)

    logger.info("✅ LangGraph workflow compiled successfully")

    return graph


# Global graph instance
agent_graph = build_agent_graph()
