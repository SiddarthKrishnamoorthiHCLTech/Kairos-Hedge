"""Loguru-based logging setup for KAIROS-HEDGE."""

import sys
from pathlib import Path

from loguru import logger

_LOG_DIR = Path("output/logs")
_LOG_DIR.mkdir(parents=True, exist_ok=True)

logger.remove()

logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{name}</cyan> — {message}",
    colorize=True,
)

logger.add(
    _LOG_DIR / "kairos_hedge_{time:YYYY-MM-DD}.log",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} — {message}",
    rotation="1 week",
    retention="4 weeks",
    compression="zip",
)


def get_logger(name: str = "kairos_hedge") -> "logger":
    """Return a contextualised logger instance."""
    return logger.bind(name=name)
