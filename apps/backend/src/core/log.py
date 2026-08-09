import logging

from rich.logging import RichHandler


def setup_logging(level: int) -> None:
    rich = RichHandler(rich_tracebacks=True)

    logging.basicConfig(
        level=level,
        handlers=[rich],
        format="%(name)s %(funcName)s() %(lineno)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Suppress verbose HTTP libraries
    for logger_name in ("httpcore", "httpx", "hpack", "urllib3", "anthropic"):
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
