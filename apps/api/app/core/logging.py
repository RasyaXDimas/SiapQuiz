"""Logging terstruktur SiapQuiz.

structlog JSON, satu baris per peristiwa, nama event bergaya titik
(mis. ``ping.received``). Processor menempelkan ``request_id`` dari contextvar
dan meredaksi nilai sensitif sebelum ditulis ke log.
"""

import logging
from collections.abc import MutableMapping
from contextvars import ContextVar
from typing import Any

import structlog

from app.core.config import settings

# ContextVar tempat middleware request_id menyimpan nilai; dibaca processor.
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def add_request_id(
    logger: structlog.stdlib.BoundLogger,
    method_name: str,
    event_dict: MutableMapping[str, Any],
) -> MutableMapping[str, Any]:
    """Tempelkan request_id dari contextvar ke setiap peristiwa log."""
    event_dict["request_id"] = request_id_var.get()
    return event_dict


# Key yang nilai-nilainya wajib dihapus dari log — rahasia tidak pernah keluar
# (AGENTS.md hard rule #10, coding-standard.md §3.5).
SENSITIVE_KEYS = {"password", "api_key", "token", "authorization", "ciphertext"}


def redact_sensitive(
    logger: structlog.stdlib.BoundLogger,
    method_name: str,
    event_dict: MutableMapping[str, Any],
) -> MutableMapping[str, Any]:
    """Redaksi nilai untuk key yang menyangkut rahasia (recursive)."""
    for key in list(event_dict.keys()):
        if key.lower() in SENSITIVE_KEYS:
            event_dict[key] = "[REDACTED]"
        elif isinstance(event_dict[key], dict):
            event_dict[key] = redact_sensitive(logger, method_name, event_dict[key])
    return event_dict


def setup_logging() -> None:
    """Pasang handler logging + konfigurasi structlog sekali saat import."""
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(format="%(message)s", level=level)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            add_request_id,
            redact_sensitive,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


setup_logging()


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    logger: structlog.stdlib.BoundLogger = structlog.get_logger(name)
    return logger
