import logging
from logging import StreamHandler


def setup_logging() -> None:
    logging.getLogger("uvicorn.error").disabled = True
    logging.basicConfig(
        handlers=[StreamHandler()],
        format="%(levelname)s %(asctime)s %(name)s %(funcName)s() %(lineno)s: %(message)s",
    )
