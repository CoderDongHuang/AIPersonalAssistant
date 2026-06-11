"""
Intent Recognition Node

Parses user natural language input to identify the intended action
"""

from typing import Dict, Any
from models.agent_state import AgentState
from config import settings
from loguru import logger
import json

try:
    from openai import OpenAI
except ImportError:
    logger.warning("OpenAI SDK not installed, using mock implementation")
    OpenAI = None


INTENT_RECOGNITION_PROMPT = """你是一个智能日历助手的意图识别模块。分析用户输入，识别其意图。

支持的意图类型：
1. query_events - 查询日历事件（如："明天有什么安排？"）
2. reschedule_event - 重新安排会议（如："把周三的会议改到周五"）
3. create_event - 创建新事件（如："下周一上午10点开会"）
4. update_event - 更新事件信息（如："把会议室改成A"）
5. delete_event - 删除事件（如："取消明天的会议"）

输出JSON格式：
{{
    "action": "意图类型",
    "confidence": 0.0-1.0,
    "parameters": {{
        "event_name": "事件名称（如果有）",
        "source_time": "原始时间描述（如果是改期）",
        "target_time": "目标时间描述（如果是改期）",
        "date": "日期描述",
        "time": "时间描述",
        "attendees": ["参会人列表"],
        "location": "地点"
    }}
}}

用户输入：{user_input}

请分析并输出JSON："""


def intent_recognition_node(state: AgentState) -> Dict[str, Any]:
    """
    Intent recognition node

    Args:
        state: Current agent state with user_input

    Returns:
        Updated state with parsed intent
    """
    user_input = state.get("user_input", "")

    logger.info(f"🔍 Recognizing intent for: {user_input}")

    try:
        # Try to use LLM for intent recognition
        api_key = settings.get_llm_api_key()
        if OpenAI and api_key:
            intent = _recognize_with_llm(user_input)
        else:
            # Fallback to rule-based recognition
            logger.info("Using rule-based intent recognition (no API key configured)")
            intent = _recognize_with_rules(user_input)

        action = intent.get("action", "unknown")
        confidence = intent.get("confidence", 0.0)
        parameters = intent.get("parameters", {})

        # Ensure action is always available in the parameters/intent dict
        # (LLM may put it only at top level; rule-based includes it in parameters)
        if "action" not in parameters:
            parameters["action"] = action

        logger.info(f"✅ Intent recognized: {action} (confidence: {confidence})")

        return {
            "intent": parameters,
            "intent_confidence": confidence,
            "should_continue": True
        }

    except Exception as e:
        logger.error(f"❌ Intent recognition failed: {e}")
        return {
            "intent": None,
            "intent_confidence": 0.0,
            "errors": [f"Intent recognition error: {str(e)}"],
            "should_continue": False
        }



def _recognize_with_llm(user_input: str) -> Dict[str, Any]:
    """Use OpenAI-compatible API (DeepSeek) for intent recognition"""

    try:
        # Create client — use explicit http_client to avoid httpx 0.28 proxy issues
        import httpx
        http_client = httpx.Client(proxy=None) if hasattr(httpx, 'Client') else None

        client_kwargs = {
            "api_key": settings.get_llm_api_key(),
            "base_url": settings.get_openai_base_url(),
        }
        if http_client is not None:
            client_kwargs["http_client"] = http_client

        client = OpenAI(**client_kwargs)

        prompt = INTENT_RECOGNITION_PROMPT.format(user_input=user_input)

        response = client.chat.completions.create(
            model=settings.get_llm_model(),
            messages=[
                {"role": "system", "content": "你是一个专业的意图识别助手，只输出JSON格式的结果。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )

        result_text = response.choices[0].message.content.strip()

        # Remove markdown code fences if present
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]

        # Parse JSON
        intent = json.loads(result_text.strip())
        return intent

    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse LLM response as JSON, falling back to rules: {e}")
        return _recognize_with_rules(user_input)

    except Exception as e:
        # API call or client creation error — gracefully fall back to rules
        logger.warning(f"LLM unavailable ({type(e).__name__}: {e}), using rule-based recognition")
        return _recognize_with_rules(user_input)


def _recognize_with_rules(user_input: str) -> Dict[str, Any]:
    """Simple rule-based intent recognition (fallback)"""

    user_input_lower = user_input.lower()

    # Simple keyword matching — order matters: check create/delete before query
    import re

    if any(word in user_input_lower for word in ["改到", "改在", "调整", "移到", "换到"]):
        # Extract event name and times from input
        event_name = ""
        source_time = ""
        target_time = ""

        # Simple extraction - can be improved
        if "会议" in user_input:
            event_name = "会议"

        # Try to extract time expressions
        time_patterns = re.findall(r'(?:下|这|本)?周[一二三四五六日]|[明后]天|今天', user_input)
        if len(time_patterns) >= 2:
            source_time = time_patterns[0]
            target_time = time_patterns[1]
        elif len(time_patterns) == 1:
            target_time = time_patterns[0]
        else:
            # Default values if no explicit time found
            source_time = "周三"
            target_time = "周五"

        return {
            "action": "reschedule_event",
            "confidence": 0.6,
            "parameters": {
                "action": "reschedule_event",
                "event_name": event_name or "会议",
                "source_time": source_time,
                "target_time": target_time
            }
        }

    elif any(word in user_input_lower for word in ["创建", "新建", "添加", "安排一个", "安排个", "预定"]):
        return {
            "action": "create_event",
            "confidence": 0.6,
            "parameters": {
                "action": "create_event",
                "event_name": "",
                "date": user_input
            }
        }

    elif any(word in user_input_lower for word in ["删除", "取消", "移除"]):
        return {
            "action": "delete_event",
            "confidence": 0.6,
            "parameters": {
                "action": "delete_event",
                "event_name": ""
            }
        }

    elif any(word in user_input_lower for word in ["有什么", "查询", "查看", "日程", "安排"]):
        return {
            "action": "query_events",
            "confidence": 0.6,
            "parameters": {
                "action": "query_events",
                "date": user_input
            }
        }

    else:
        return {
            "action": "unknown",
            "confidence": 0.3,
            "parameters": {
                "action": "unknown"
            }
        }
