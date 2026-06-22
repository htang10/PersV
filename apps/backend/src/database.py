import logging

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from src.core.config import settings
from src.pipeline.exceptions import ConnectionNotFoundError, DBConfigError

logger = logging.getLogger(__name__)


class DBConnectionManager:
    def __init__(self) -> None:
        self._engines = None  # Assume one user for now
        self._db_name = None

    def check_connection(self) -> None:
        engine = create_engine(str(settings.DATABASE_URL))
        with Session(engine) as session:
            session.execute(text("SELECT 1"))

    def connect(self, connection_string: str, db_name: str) -> None:
        if self.is_connected():
            self.disconnect()

        engine = create_engine(
            connection_string,
            pool_size=1,
            max_overflow=0,
            pool_pre_ping=True,
            pool_recycle=3600,
        )

        try:
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except OperationalError as e:
            engine.dispose()
            logger.error(e)
            raise DBConfigError

        self._engines = engine
        self._db_name = db_name

    def get_db_name(self) -> str | None:
        return self._db_name

    def get_engine(self) -> Engine:
        try:
            return self._engines
        except KeyError as e:
            logger.error("Failed due to 'self._engine' being None")
            raise ConnectionNotFoundError

    def disconnect(self) -> None:
        try:
            self._engines.dispose()
            self._engines = None
        except AttributeError as e:
            logger.error("Failed due to 'self._engine' being None")
            raise ConnectionNotFoundError

    def is_connected(self) -> bool:
        return self._engines


conn_manager = DBConnectionManager()
