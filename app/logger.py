"""
Shared logging configuration.
"""

import logging
import sys

from app.config import settings

_configured = False


def _configure_root() -> None:
    global _configured
    if _configured:
        return
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stdout,
    )
    _configured = True


def get_logger(name: str) -> logging.Logger:
    _configure_root()
    return logging.getLogger(name)
