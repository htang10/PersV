import logging
from logging import StreamHandler


def setup_logging(level: str) -> None:
    handler = StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            "%(levelname)s %(asctime)s %(name)s %(funcName)s() %(lineno)s: %(message)s"
        )
    )

    logging.basicConfig(level=level, handlers=[handler])

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers = [handler]
        uvicorn_logger.propagate = False
