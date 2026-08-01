"""
logger.py

Centralized logging configuration for the Daily Aptitude Generator.
"""

from __future__ import annotations

import logging
from pathlib import Path

from src.config import settings
from src.utils.helpers import ensure_directory


_LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)

_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


_CONFIGURED = False


def configure_logging() -> None:
    """Configure application logging.

    Creates:
        - Console logging
        - File logging

    Logging is configured only once.
    """

    global _CONFIGURED

    if _CONFIGURED:
        return


    log_directory: Path = ensure_directory(
        settings.paths.logs_dir
    )


    log_file = (
        log_directory
        / settings.logging.filename
    )


    log_level = getattr(
        logging,
        settings.logging.level.upper(),
        logging.INFO,
    )


    formatter = logging.Formatter(
        fmt=_LOG_FORMAT,
        datefmt=_DATE_FORMAT,
    )


    file_handler = logging.FileHandler(
        log_file,
        encoding="utf-8",
    )

    file_handler.setFormatter(
        formatter
    )


    console_handler = logging.StreamHandler()

    console_handler.setFormatter(
        formatter
    )


    root_logger = logging.getLogger()

    root_logger.setLevel(
        log_level
    )


    root_logger.handlers.clear()


    root_logger.addHandler(
        file_handler
    )

    root_logger.addHandler(
        console_handler
    )


    _CONFIGURED = True



def get_logger(
    name: str,
) -> logging.Logger:
    """Return a configured logger.

    Args:
        name:
            Logger name, generally ``__name__``.

    Returns:
        logging.Logger:
            Configured logger instance.
    """

    configure_logging()

    return logging.getLogger(name)