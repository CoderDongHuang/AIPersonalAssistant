"""
日志系统配置
使用 loguru 提供结构化、彩色的日志输出
"""

import sys
from pathlib import Path
from loguru import logger
from config.settings import settings


def setup_logging():
    """
    配置日志系统

    Features:
    - 控制台彩色输出
    - 文件日志记录（按日期轮转）
    - 错误日志单独记录
    - 结构化JSON格式（生产环境）
    """

    # 移除默认的 handler
    logger.remove()

    # 创建 logs 目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # 控制台日志 - 开发环境友好格式
    logger.add(
        sys.stderr,
        level=settings.LOG_LEVEL,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        colorize=True,
        backtrace=True,
        diagnose=settings.is_development()
    )

    # 文件日志 - 所有级别，按天轮转，保留30天
    logger.add(
        log_dir / "app_{time:YYYY-MM-DD}.log",
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="00:00",
        retention="30 days",
        compression="zip",
        enqueue=True,
        encoding="utf-8"
    )

    # 错误日志 - 单独记录 ERROR 及以上级别
    logger.add(
        log_dir / "error_{time:YYYY-MM-DD}.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="00:00",
        retention="90 days",
        compression="zip",
        enqueue=True,
        encoding="utf-8"
    )

    # 生产环境添加 JSON 格式日志（便于日志分析）
    if settings.is_production():
        logger.add(
            log_dir / "json_{time:YYYY-MM-DD}.log",
            level=settings.LOG_LEVEL,
            format="{message}",
            serialize=True,
            rotation="00:00",
            retention="90 days",
            encoding="utf-8"
        )

    logger.info("日志系统初始化完成 | Level: {} | Environment: {}",
                settings.LOG_LEVEL, settings.APP_ENV)


# 导出配置好的 logger
__all__ = ["logger", "setup_logging"]