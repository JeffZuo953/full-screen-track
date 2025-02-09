# Standard library imports
from __future__ import annotations
import logging
import datetime
from pathlib import Path

# Local application/library specific imports
from src.core.manager.config import ConfigManager

# Global variable to track if the logger has been set up
logger_setup: bool = False


def setup_logger() -> logging.Logger:
    """
    Configure and return the application-wide logger.
    """
    global logger_setup

    if logger_setup:
        # If the logger has already been set up, return the existing logger
        return logging.getLogger("full screen tracker")

    date: str = datetime.datetime.now().strftime("%Y-%m-%d")
    log_dir: Path = Path("./log")
    log_dir.mkdir(exist_ok=True)  # Create log directory if it doesn't exist

    logger: logging.Logger = logging.getLogger("full screen tracker")

    config_manager: ConfigManager = ConfigManager.get_instance()
    logger.setLevel(
        config_manager.get_log_config().get("level", logging.INFO).upper()
    )  # Set logger to the lowest level

    if not logger.handlers:
        # File handler
        try:
            file_handler: logging.FileHandler = logging.FileHandler(
                log_dir / f"{date}.log", encoding="utf-8"
            )
            config_log_level: str = (
                config_manager.get_log_config().get("level", logging.DEBUG).upper()
            )
            file_handler.setLevel(
                config_log_level
            )  # Set file handler to debug level
        except Exception as e:
            logger.error(f"Failed to get log level from config: {e}")
            file_handler.setLevel(logging.DEBUG)  # Set file handler to debug level

        # Formatter
        formatter: logging.Formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Set the global variable to indicate that the logger has been set up
    logger_setup = True

    return logger


# Initialize logger without GUI handler
logger: logging.Logger = setup_logger()
