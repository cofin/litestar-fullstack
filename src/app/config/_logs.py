from __future__ import annotations

import logging
from typing import Any

import structlog
from litestar.logging.config import LoggingConfig

from app.config._settings import settings
from app.lib.log import configure, default_processors, stdlib_processors

logs = LoggingConfig(
    root={"level": logging.getLevelName(settings.LOG_LEVEL), "handlers": ["queue_listener"]},
    formatters={
        "standard": {"()": structlog.stdlib.ProcessorFormatter, "processors": stdlib_processors},
    },
    loggers={
        "uvicorn.access": {
            "propagate": False,
            "level": settings.LOG_UVICORN_ACCESS_LEVEL,
            "handlers": ["queue_listener"],
        },
        "uvicorn.error": {
            "propagate": False,
            "level": settings.LOG_UVICORN_ERROR_LEVEL,
            "handlers": ["queue_listener"],
        },
        "saq": {
            "propagate": False,
            "level": settings.LOG_SAQ_LEVEL,
            "handlers": ["queue_listener"],
        },
        "sqlalchemy.engine": {
            "propagate": False,
            "level": settings.LOG_SQLALCHEMY_LEVEL,
            "handlers": ["queue_listener"],
        },
        "sqlalchemy.pool": {
            "propagate": False,
            "level": settings.LOG_SQLALCHEMY_LEVEL,
            "handlers": ["queue_listener"],
        },
    },
)
"""Pre-configured log config for application deps.

While we use structlog for internal app logging, we still want to ensure
that logs emitted by any of our dependencies are handled in a non-
blocking manner.
"""


def get_logger(*args: Any, **kwargs: Any) -> structlog.BoundLogger:
    """Return a configured logger for the given name.

    Returns:
        Logger: A configured logger instance
    """
    logs.configure()
    configure(default_processors)  # type: ignore[arg-type]
    return structlog.getLogger(*args, **kwargs)  # type: ignore
