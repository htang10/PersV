import json
import logging
import sys
from contextvars import ContextVar
from logging import LogRecord
from typing import Any

from rich.logging import RichHandler

from src.core.config import settings

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


original_factory = logging.getLogRecordFactory()


def record_factory(
    *args: Any,
    **kwargs: Any,
) -> LogRecord:
    record = original_factory(*args, **kwargs)
    record.request_id = request_id_var.get()
    return record


class JsonFormatter(logging.Formatter):
    """One JSON object per record, so Cloud Logging keeps multi-line messages together."""

    def format(self, record: logging.LogRecord) -> str:
        message = record.getMessage()
        if record.exc_info:
            message += "\n" + self.formatException(record.exc_info)
        return json.dumps(
            {
                "severity": record.levelname,  # Cloud Logging reads this field
                "request_id": getattr(record, "request_id", None),
                "message": message,
                "logger": record.name,
                "function": record.funcName,
                "line": record.lineno,
                "process": record.process,
                "thread": record.threadName,
            }
        )


def setup_logging(level: int) -> None:
    if settings.DEBUG:
        handler = RichHandler(rich_tracebacks=True)
        handler.setFormatter(
            logging.Formatter(
                "%(process)d %(processName)s %(thread)d %(threadName)s "
                "%(name)s %(funcName)s() %(lineno)s: %(message)s"
            )
        )
    else:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())

    logging.setLogRecordFactory(record_factory)
    logging.basicConfig(level=level, handlers=[handler], force=True)

    # Suppress verbose HTTP libraries
    for logger_name in (
        "httpcore",
        "httpcore2",
        "httpx",
        "httpx2",
        "hpack",
        "urllib3",
        "openai",
    ):
        logging.getLogger(logger_name).setLevel(max(level, logging.WARNING))

    uvicorn_loggers = (
        ("uvicorn", level),
        ("uvicorn.error", level),
    )

    for logger_name, log_level in uvicorn_loggers:
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.propagate = True
        logger.setLevel(log_level)
