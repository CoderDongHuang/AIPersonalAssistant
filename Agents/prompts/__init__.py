"""
Prompt模板模块

包含所有LLM交互的prompt模板
"""

from agents.prompts.intent_prompt import INTENT_RECOGNITION_PROMPT
from agents.prompts.planning_prompt import TASK_PLANNING_PROMPT

__all__ = [
    "INTENT_RECOGNITION_PROMPT",
    "TASK_PLANNING_PROMPT"
]