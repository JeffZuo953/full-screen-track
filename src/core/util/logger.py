import logging
import datetime
from pathlib import Path

from src.core.manager.config import ConfigManager

# 全局变量，用于跟踪日志记录器是否已经被设置
logger_setup = False


def setup_logger() -> logging.Logger:
    """Configure and return the application-wide logger"""
    global logger_setup

    if logger_setup:
        # 如果日志记录器已经被设置，直接返回现有的日志记录器
        return logging.getLogger("full screen tracker")

    date = datetime.datetime.now().strftime("%Y-%m-%d")
    log_dir = Path("./log")
    log_dir.mkdir(exist_ok=True)

    logger = logging.getLogger("full screen tracker")

    config_manager = ConfigManager.get_instance()
    logger.setLevel(config_manager.get_log_config().get("level", logging.INFO).upper())  # Set logger to the lowest level

    if not logger.handlers:
        # File handler
        try:
            file_handler = logging.FileHandler(
                log_dir / f"{date}.log", encoding="utf-8"
            )
            config_log_level = (
                config_manager.get_log_config().get("level", logging.DEBUG).upper()
            )
            file_handler.setLevel(config_log_level)  # Set file handler to debug level
        except Exception as e:
            logger.error(f"Failed to get log level from config: {e}")
            file_handler.setLevel(logging.DEBUG)  # Set file handler to debug level

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # 设置全局变量，表示日志记录器已经被设置
    logger_setup = True

    return logger


# Initialize logger without GUI handler
logger: logging.Logger = setup_logger()
