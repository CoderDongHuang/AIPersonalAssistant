"""
Personal AI Assistant - 主入口文件

基于自然语言的个人效率助手，集成Google Calendar与Gmail API。
支持复杂时间推理和冲突检测，通过Function Calling实现多工具协同。

Usage:
    python main.py
"""

import sys
from loguru import logger
from config import setup_logging, settings


def check_dependencies():
    """检查依赖项是否正确安装"""
    try:
        import langchain
        import langgraph
        import openai
        from google.oauth2.credentials import Credentials
        logger.info("✅ 所有依赖项检查通过")
        return True
    except ImportError as e:
        logger.error(f"❌ 缺少依赖: {e}")
        logger.error("请运行: pip install -r requirements.txt")
        return False


def check_environment():
    """检查环境变量配置"""
    missing_vars = []

    required_vars = [
        "OPENAI_API_KEY",
        "GOOGLE_PROJECT_ID",
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET"
    ]

    for var in required_vars:
        if not hasattr(settings, var) or not getattr(settings, var):
            missing_vars.append(var)

    if missing_vars:
        logger.warning("⚠️  以下环境变量未配置:")
        for var in missing_vars:
            logger.warning(f"   - {var}")
        logger.warning("请复制 .env.example 为 .env 并填写配置")
        return False

    logger.info("✅ 环境变量检查通过")
    return True


def main():
    """主函数"""
    # 初始化日志系统
    setup_logging()

    logger.info("=" * 60)
    logger.info("🤖 Personal AI Assistant 启动中...")
    logger.info("=" * 60)

    # 检查依赖
    if not check_dependencies():
        sys.exit(1)

    # 检查环境
    if not check_environment():
        sys.exit(1)

    logger.info(f"📊 当前环境: {settings.APP_ENV}")
    logger.info(f"🕐 默认时区: {settings.DEFAULT_TIMEZONE}")
    logger.info(f"🤖 OpenAI模型: {settings.OPENAI_MODEL}")

    # TODO: 后续在这里初始化Agent和工作流
    logger.info("✨ Personal AI Assistant 已就绪！")
    logger.info("⚠️  Agent功能开发中，敬请期待...")

    print("\n" + "=" * 60)
    print("🎉 Personal AI Assistant v1.0")
    print("=" * 60)
    print("\n项目初始化完成！")
    print("\n下一步:")
    print("  1. 配置 Google API 认证")
    print("  2. 实现核心工具模块")
    print("  3. 构建 LangGraph 工作流")
    print("\n详细文档请查看: 技术方案文档.md")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()