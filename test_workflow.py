from agents.graph_builder import build_agent_graph
from loguru import logger

def test_basic_workflow():
    """测试基本工作流构建"""
    try:
        graph = build_agent_graph()
        logger.info("✅ 工作流构建成功！")

        # 测试一个简单的输入
        initial_state = {
            "user_input": "帮我把下周三的会议改到周五",
            "intent": None,
            "intent_confidence": 0.0,
            "parsed_times": None,
            "source_time": None,
            "target_time": None,
            "source_event": None,
            "target_slot": None,
            "conflicts": [],
            "conflict_result": None,
            "action_plan": None,
            "execution_results": [],
            "errors": [],
            "email_sent": False,
            "email_recipients": [],
            "response": "",
            "needs_user_confirmation": False,
            "should_continue": False
        }

        # 运行工作流 - 需要提供 configurable 配置
        config = {
            "configurable": {
                "thread_id": "test_thread_1"
            }
        }

        result = graph.invoke(initial_state, config=config)
        logger.info(f"✅ 工作流执行完成！")
        logger.info(f"响应: {result.get('response')}")

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_basic_workflow()
