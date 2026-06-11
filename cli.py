"""
CLI 命令行交互界面

提供用户友好的命令行接口来与AI助理交互。
基于 rich 库实现彩色输出和状态提示。
"""

import sys
import uuid
import os
from typing import Optional

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.spinner import Spinner
from rich.live import Live
from rich.text import Text
from rich import box

from config import setup_logging, settings

# Force UTF-8 encoding on Windows to support emoji and Chinese output
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    # Reconfigure stdout/stderr for UTF-8
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

console = Console(highlight=False)


# ═══════════════════════════════════════════════════════════════════════════════
# Display helpers
# ═══════════════════════════════════════════════════════════════════════════════

def display_welcome():
    """Show welcome banner."""
    console.print()
    console.print(Panel(
        "[bold cyan]🤖 Personal AI Assistant[/bold cyan]\n"
        "[dim]Calendar & Email Automation — 基于自然语言的个人效率助手[/dim]",
        border_style="cyan",
        padding=(1, 2),
    ))
    console.print("[bold]我可以帮你:[/bold]")
    console.print("  📅 查询和管理日历事件")
    console.print("  ⏰ 调整会议时间")
    console.print("  📧 发送邮件通知参会人")
    console.print("  ⚠️  检测时间冲突并推荐备选时间")
    console.print()
    console.print("[dim]输入 [/dim][bold]help[/bold][dim] 查看帮助，[/dim][bold]quit[/bold][dim] 退出[/dim]")
    console.print()


def display_help():
    """Show help information."""
    help_table = Table(box=box.ROUNDED, show_header=False, border_style="blue")
    help_table.add_column("命令", style="bold cyan", width=20)
    help_table.add_column("说明", style="white")

    help_table.add_row("help, h, ?", "显示此帮助信息")
    help_table.add_row("status", "查看系统状态和配置")
    help_table.add_row("events", "显示当前示例日历事件")
    help_table.add_row("quit, exit, q", "退出程序")
    help_table.add_row("")
    help_table.add_row("[bold yellow]自然语言指令示例:[/bold yellow]")
    help_table.add_row("", "")
    help_table.add_row("  • 明天有什么安排？", "查询明天的日程")
    help_table.add_row("  • 帮我把下周三的会议改到周五", "重新安排会议时间")
    help_table.add_row("  • 下周一上午10点开团队周会", "创建新事件")
    help_table.add_row("  • 取消明天的会议", "删除事件")

    console.print()
    console.print(Panel(help_table, title="📖 帮助", border_style="blue"))
    console.print()


def display_status():
    """Show system status."""
    table = Table(box=box.ROUNDED, show_header=False, border_style="green")
    table.add_column("项目", style="bold cyan")
    table.add_column("值", style="white")

    table.add_row("环境", settings.APP_ENV)
    table.add_row("日志级别", settings.LOG_LEVEL)
    table.add_row("时区", settings.DEFAULT_TIMEZONE)
    table.add_row("LLM模型", settings.get_llm_model() or "[dim]未配置（规则匹配模式）[/dim]")
    table.add_row("LLM可用", "✅" if settings.get_llm_api_key() else "⚠️ 未配置")
    table.add_row("邮件通知",
                  f"{'✅ 已配置' if settings.EMAIL_SENDER else '⚠️ 未配置（优雅降级）'}")
    table.add_row("日历存储", "SQLite (calendar.db)")

    console.print()
    console.print(Panel(table, title="📊 系统状态", border_style="green"))
    console.print()


def display_events():
    """Show current sample/seed events in the calendar."""
    from services.local_calendar import LocalCalendarService
    from datetime import datetime, timedelta

    cal = LocalCalendarService()
    now = datetime.now()
    events = cal.list_events(now - timedelta(days=1), now + timedelta(days=30))

    if not events:
        console.print("[yellow]📅 当前没有日历事件[/yellow]")
        return

    table = Table(box=box.ROUNDED, border_style="magenta")
    table.add_column("ID", style="dim", width=8)
    table.add_column("标题", style="bold cyan")
    table.add_column("时间", style="yellow")
    table.add_column("参会人", style="green")

    for e in events:
        start = e["start_time"]
        end = e["end_time"]
        if hasattr(start, "strftime"):
            time_str = f"{start.strftime('%m/%d %H:%M')} - {end.strftime('%H:%M')}"
        else:
            time_str = str(start)
        attendees = ", ".join(e.get("attendees", [])[:2])
        if len(e.get("attendees", [])) > 2:
            attendees += f" +{len(e['attendees']) - 2}"

        table.add_row(e["id"], e["title"], time_str, attendees)

    console.print()
    console.print(Panel(table, title="📅 日历事件", border_style="magenta"))
    console.print()


# ═══════════════════════════════════════════════════════════════════════════════
# Agent integration
# ═══════════════════════════════════════════════════════════════════════════════

def run_agent(user_input: str) -> str:
    """
    Run the LangGraph agent workflow on a user input.

    Args:
        user_input: Natural language command from the user.

    Returns:
        The agent's response string.
    """
    from agents.graph_builder import build_agent_graph
    from tests.fixtures.sample_data import get_initial_agent_state

    # Build initial state
    initial_state = get_initial_agent_state(user_input)

    # Build graph (uses global singleton after first call)
    graph = build_agent_graph()

    config = {
        "configurable": {
            "thread_id": f"cli_{uuid.uuid4().hex[:8]}"
        }
    }

    logger.info(f"🚀 Running agent workflow for: {user_input}")

    try:
        result = graph.invoke(initial_state, config=config)
    except Exception as e:
        logger.error(f"Agent workflow failed: {e}")
        return f"❌ Agent 工作流执行失败: {str(e)}"

    response = result.get("response", "")
    errors = result.get("errors", [])

    if errors and not response:
        response = "❌ 处理遇到问题，请重试"

    logger.info(f"✅ Agent response: {response[:100]}...")
    return response


# ═══════════════════════════════════════════════════════════════════════════════
# Interactive mode
# ═══════════════════════════════════════════════════════════════════════════════

def interactive_mode():
    """Main interactive loop."""
    display_welcome()

    while True:
        try:
            console.print("[bold green]💬 请输入指令:[/bold green] ", end="")
            user_input = input().strip()

            if not user_input:
                continue

            # ── Built-in commands ──
            if user_input.lower() in ['quit', 'exit', 'q']:
                console.print()
                console.print("[yellow]👋 再见！期待下次使用~[/yellow]")
                console.print()
                break

            elif user_input.lower() in ['help', 'h', '?']:
                display_help()
                continue

            elif user_input.lower() == 'status':
                display_status()
                continue

            elif user_input.lower() == 'events':
                display_events()
                continue

            # ── Natural language → Agent workflow ──
            console.print()
            with console.status("[bold cyan]🤔 正在处理中...[/bold cyan]", spinner="dots"):
                response = run_agent(user_input)

            # Display the response in a panel
            _display_response(response)

        except KeyboardInterrupt:
            console.print()
            console.print("[yellow]👋 已退出 (Ctrl+C)[/yellow]")
            console.print()
            break
        except EOFError:
            console.print()
            console.print("[yellow]👋 输入已关闭，退出程序[/yellow]")
            console.print()
            break


def _display_response(response: str):
    """Format and display the agent's response."""
    # Determine panel style based on content
    if response.startswith("✅"):
        style = "green"
    elif response.startswith("❌"):
        style = "red"
    elif response.startswith("⚠️"):
        style = "yellow"
    elif response.startswith("📅"):
        style = "cyan"
    else:
        style = "white"

    console.print(Panel(
        response,
        border_style=style,
        padding=(1, 2),
    ))
    console.print()


# ═══════════════════════════════════════════════════════════════════════════════
# Single-command mode
# ═══════════════════════════════════════════════════════════════════════════════

def run_single_command(command: str):
    """Run a single command and exit (non-interactive mode)."""
    from config import setup_logging
    setup_logging()

    console.print()
    console.print(f"[dim]💬 指令:[/dim] {command}")
    console.print()

    with console.status("[bold cyan]🤔 正在处理...[/bold cyan]", spinner="dots"):
        response = run_agent(command)

    _display_response(response)


# ═══════════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """CLI entry point — supports interactive mode or single-command mode."""
    setup_logging()
    logger.info("CLI 界面启动")

    if len(sys.argv) > 1:
        # Single-command mode: python cli.py "帮我把周三的会议改到周五"
        command = " ".join(sys.argv[1:])

        if command.lower() in ['help', 'h']:
            display_help()
        elif command.lower() == 'status':
            display_status()
        elif command.lower() == 'events':
            display_events()
        else:
            run_single_command(command)
    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()
