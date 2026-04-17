"""Logging setup for the Triple Flow Simulator."""
import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    """Configure root logger.

    Args:
        level: Logging level name (DEBUG, INFO, WARNING, ERROR).
    """
    level_num = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=level_num,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stderr,
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
