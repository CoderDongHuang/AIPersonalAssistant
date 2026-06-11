"""
Personal AI Assistant — 主入口文件

基于自然语言的个人效率助手，本地SQLite日历 + SMTP邮件 + DeepSeek LLM。
支持复杂时间推理和冲突检测，通过LangGraph构建有状态Agent工作流。

Usage:
    python main.py                        # 交互式模式
    python main.py "明天有什么安排？"       # 单指令模式
    python main.py --check                # 检查环境配置
"""

import sys
from loguru import logger
from config import setup_logging, settings


def check_environment():
    """Check environment configuration and print a summary."""
    issues = []

    # Check LLM
    if settings.get_llm_api_key():
        logger.info(f"✅ LLM已配置: {settings.get_llm_model()}")
    else:
        logger.warning("⚠️  LLM未配置，将使用规则匹配降级模式")

    # Check email
    if settings.EMAIL_SENDER:
        logger.info(f"✅ 邮件已配置: {settings.EMAIL_SENDER}")
    else:
        logger.info("ℹ️  邮件未配置，通知功能将优雅降级")

    return True


def run_interactive():
    """Launch the interactive CLI."""
    from cli import interactive_mode
    interactive_mode()


def run_single_command(command: str):
    """Run a single command via the agent and print the result."""
    from cli import run_single_command
    run_single_command(command)


def main():
    """Main entry point."""
    # Initialize logging
    setup_logging()

    logger.info("=" * 60)
    logger.info("🤖 Personal AI Assistant 启动中...")
    logger.info("=" * 60)

    # Check environment silently
    check_environment()

    logger.info(f"📊 环境: {settings.APP_ENV} | 时区: {settings.DEFAULT_TIMEZONE}")
    logger.info(f"🤖 LLM: {settings.get_llm_model() or '规则匹配模式'}")
    logger.info(f"📧 邮件: {'已配置' if settings.EMAIL_SENDER else '未配置'}")

    # Parse command-line arguments
    if len(sys.argv) > 1:
        first_arg = sys.argv[1]

        if first_arg in ['--check', '-c']:
            # Environment check mode
            from verify_setup import main as verify_main
            sys.exit(verify_main())
        elif first_arg in ['--help', '-h']:
            print_usage()
        else:
            # Treat all args as a natural language command
            command = " ".join(sys.argv[1:])
            run_single_command(command)
    else:
        # Interactive mode
        run_interactive()


def print_usage():
    """Print usage information."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║           🤖 Personal AI Assistant                           ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Usage:                                                       ║
║    python main.py                 交互式模式                   ║
║    python main.py "明天有什么安排？"  单指令模式                ║
║    python main.py --check          检查环境配置                ║
║    python main.py --help           显示此帮助                  ║
║                                                               ║
║  Also available:                                              ║
║    python cli.py                   CLI 交互界面                ║
║    python test_workflow.py         工作流端到端测试            ║
║    python verify_setup.py          项目环境验证                ║
║    pytest tests/unit/ -v           运行81个单元测试            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    main()
