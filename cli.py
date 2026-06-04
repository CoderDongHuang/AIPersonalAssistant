"""
CLI 命令行交互界面

提供用户友好的命令行接口来与AI助理交互
"""

import sys
from typing import Optional
from loguru import logger


def display_welcome():
    """显示欢迎信息"""
    print("\n" + "=" * 60)
    print("🤖 Personal AI Assistant - Calendar & Email Automation")
    print("=" * 60)
    print("\n我可以帮你:")
    print("  📅 查询和管理日历事件")
    print("  ⏰ 调整会议时间")
    print("  📧 发送邮件通知")
    print("  ⚠️  检测时间冲突")
    print("\n输入 'help' 查看帮助，输入 'quit' 退出\n")


def display_help():
    """显示帮助信息"""
    help_text = """
╔═══════════════════════════════════════════════════════════╗
║                    可用命令                               ║
╠═══════════════════════════════════════════════════════════╣
║  help              显示此帮助信息                         ║
║  status            查看系统状态                           ║
║  test              测试连接                               ║
║  quit / exit       退出程序                               ║
╚═══════════════════════════════════════════════════════════╝

示例指令（开发中）:
  • "帮我把下周三下午的会议改到周五"
  • "明天上午我有什么安排？"
  • "给团队发送会议通知"
    """
    print(help_text)


def display_status():
    """显示系统状态"""
    from config import settings

    print("\n📊 系统状态:")
    print(f"  环境: {settings.APP_ENV}")
    print(f"  日志级别: {settings.LOG_LEVEL}")
    print(f"  时区: {settings.DEFAULT_TIMEZONE}")
    print(f"  OpenAI模型: {settings.OPENAI_MODEL}")
    print(f"  邮件通知: {'启用' if settings.EMAIL_NOTIFICATION_ENABLED else '禁用'}")
    print()


def interactive_mode():
    """交互式模式"""
    display_welcome()

    while True:
        try:
            user_input = input("💬 请输入指令: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 再见！期待下次使用~\n")
                break
            elif user_input.lower() in ['help', 'h', '?']:
                display_help()
            elif user_input.lower() in ['status']:
                display_status()
            elif user_input.lower() in ['test']:
                print("\n🔧 测试功能开发中...\n")
            else:
                print("\n⚠️  Agent功能正在开发中，敬请期待！\n")
                print("💡 提示: 目前仅支持基础命令 (help/status/test/quit)\n")

        except KeyboardInterrupt:
            print("\n\n👋 检测到中断信号，再见！\n")
            break
        except EOFError:
            print("\n")
            break


def main():
    """CLI入口函数"""
    from config import setup_logging
    setup_logging()

    logger.info("CLI 界面启动")

    # 检查命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == 'help':
            display_help()
        elif command == 'status':
            display_status()
        else:
            print(f"❌ 未知命令: {command}")
            print("使用 'help' 查看可用命令")
    else:
        # 进入交互模式
        interactive_mode()


if __name__ == "__main__":
    main()