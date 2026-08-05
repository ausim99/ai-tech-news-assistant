"""Loguru setup shared by backend and pipeline scripts."""

import sys

from loguru import logger

logger.remove()
logger.add(sys.stderr, level="INFO", format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}")

__all__ = ["logger"]
