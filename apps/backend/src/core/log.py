import logging

from rich.logging import RichHandler

from src.core.config import settings


def setup_logging(level: int) -> None:
    log_format = "%(process)d %(processName)s %(thread)d %(threadName)s %(name)s %(funcName)s() %(lineno)s: %(message)s"
    if settings.DEBUG:
        handler = RichHandler(rich_tracebacks=True)
    else:
        handler = logging.StreamHandler()  # plain stdout, one line per record
        # or a JSON formatter here if you want CloudWatch Insights querying
        log_format = f"%(asctime)s %(levelname)s {log_format}"

    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[handler],
        datefmt="%Y-%m-%d %H:%M:%S",
    )

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
        ("uvicorn.access", max(level, logging.INFO)),
    )

    for logger_name, log_level in uvicorn_loggers:
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.propagate = True
        logger.setLevel(log_level)
