import logging

from sqlalchemy import Engine, create_engine, inspect, text
from sqlalchemy.exc import OperationalError

from src.pipeline.exceptions import ConnectionNotFoundError, DBConfigError

logger = logging.getLogger(__name__)


class DBConnectionManager:
    def __init__(self) -> None:  # Assume one user for now
        self._dialect = None
        self._db_name = None
        self._engine = None

    def get_dialect(self) -> str:
        return self._engine.dialect.name

    def get_db_name(self) -> str | None:
        return self._db_name

    def get_engine(self) -> Engine:
        try:
            return self._engine
        except KeyError:
            logger.error("Failed due to 'self._engine' being None")
            raise ConnectionNotFoundError

    def get_tables(self) -> list[str]:
        if not self._engine:
            return []
        inspector = inspect(self._engine)
        if self._engine.dialect.name == "postgresql":
            return inspector.get_table_names(schema="public")
        return inspector.get_table_names()

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

        self._engine = engine
        self._db_name = db_name

    def disconnect(self) -> None:
        try:
            self._engine.dispose()
            self._engine = None
            self._db_name = None
        except AttributeError:
            logger.error("Failed due to 'self._engine' being None")
            raise ConnectionNotFoundError

    def is_connected(self) -> bool:
        return bool(self._engine)


conn_manager = DBConnectionManager()
