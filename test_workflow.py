"""
Workflow smoke test — standalone script

Quick end-to-end test that exercises the full LangGraph pipeline.
Can be run directly:  python test_workflow.py
Or via pytest:        pytest test_workflow.py -v
"""

from loguru import logger
from config import setup_logging


def test_basic_workflow():
    """Test that the agent graph builds and runs successfully."""
    from agents.graph_builder import build_agent_graph
    from tests.fixtures.sample_data import get_initial_agent_state

    graph = build_agent_graph()
    logger.info("✅ 工作流构建成功！")

    initial_state = get_initial_agent_state("帮我把下周三的会议改到周五")
    config = {"configurable": {"thread_id": "test_thread_1"}}

    result = graph.invoke(initial_state, config=config)

    logger.info("✅ 工作流执行完成！")
    logger.info(f"响应: {result.get('response', '')[:200]}")

    # Basic assertions
    assert result.get("response") is not None, "Should produce a response"
    assert len(result["response"]) > 0, "Response should not be empty"


def test_query_workflow():
    """Test a query-type workflow."""
    from agents.graph_builder import build_agent_graph
    from tests.fixtures.sample_data import get_initial_agent_state

    graph = build_agent_graph()
    state = get_initial_agent_state("明天上午有什么安排？")
    config = {"configurable": {"thread_id": "test_query"}}

    result = graph.invoke(state, config=config)
    response = result.get("response", "")

    logger.info(f"Query response: {response[:200]}")
    assert len(response) > 0
    assert "📅" in response or "暂无" in response


def test_workflow_with_multiple_inputs():
    """Test that the workflow handles multiple different inputs."""
    from agents.graph_builder import build_agent_graph
    from tests.fixtures.sample_data import get_initial_agent_state

    graph = build_agent_graph()
    inputs = [
        "明天有什么安排？",
        "帮我把周三的会议改到周五",
        "创建一个下周一上午10点的周会",
    ]

    for i, user_input in enumerate(inputs):
        state = get_initial_agent_state(user_input)
        config = {"configurable": {"thread_id": f"multi_{i}"}}
        result = graph.invoke(state, config=config)
        assert result.get("response") is not None, \
            f"Failed on input {i}: {user_input}"
        logger.info(f"✅ Input {i} OK: '{user_input}' → {result['response'][:80]}...")


if __name__ == "__main__":
    setup_logging()

    print("\n" + "=" * 60)
    print("🧪 Personal AI Assistant — Workflow Smoke Test")
    print("=" * 60 + "\n")

    try:
        print("1/3 Testing basic reschedule workflow...")
        test_basic_workflow()
        print("   ✅ Passed\n")

        print("2/3 Testing query workflow...")
        test_query_workflow()
        print("   ✅ Passed\n")

        print("3/3 Testing multiple inputs...")
        test_workflow_with_multiple_inputs()
        print("   ✅ Passed\n")

        print("=" * 60)
        print("🎉 All smoke tests passed!")
        print("=" * 60 + "\n")
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
