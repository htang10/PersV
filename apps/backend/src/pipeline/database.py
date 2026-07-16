import logging

from sqlalchemy import Engine, create_engine, inspect, text
from sqlalchemy.exc import OperationalError

from src.pipeline.config import pl_settings
from src.pipeline.exceptions import ConnectionNotFoundError, DBConfigError

logger = logging.getLogger(__name__)


class DBConnectionManager:
    """Manages the active database connection for a user session."""

    def __init__(self) -> None:  # Assume one user for now
        self._dialect = None
        self._db_name = None
        self._engine = None

    def get_dialect(self) -> str:
        """Returns the dialect name of the active database connection."""
        return self._engine.dialect.name

    def get_db_name(self) -> str | None:
        """Returns the name of the currently connected database."""
        return self._db_name

    def get_engine(self) -> Engine:
        """Returns the active SQLAlchemy engine.

        Raises:
            ConnectionNotFoundError: If no database connection exists.
        """
        if not self._engine:
            logger.error("Failed due to 'self._engine' being None.")
            raise ConnectionNotFoundError
        return self._engine

    def get_tables(self) -> list[str]:
        """Returns the list of table names in the connected database."""
        if not self._engine:
            return []
        inspector = inspect(self._engine)
        return inspector.get_table_names()

    def connect(self, connection_string: str, db_name: str) -> None:
        """Creates and validates a database connection.

        Existing connections are closed before establishing a new one.

        Raises:
            DBConfigError: If the connection configuration is invalid or the
                database cannot be reached.
        """
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
        """Closes the active database connection.

        Raises:
            ConnectionNotFoundError: If no database connection exists.
        """
        if not self._engine:
            logger.error("Failed due to 'self._engine' being None.")
            raise ConnectionNotFoundError

        self._engine.dispose()
        self._engine = None
        self._db_name = None

    def is_connected(self) -> bool:
        """Checks whether a database connection is currently active."""
        return bool(self._engine)


conn_manager = DBConnectionManager()
