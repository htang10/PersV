from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from src.pipeline.exceptions import ConnectionNotFoundError, DBConfigError


class DBConnectionManager:
    def __init__(self):
        self._engines = None  # Assume one user for now

    def connect(self, connection_string: str):
        if not self.is_connected():
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
            except (OperationalError, Exception) as e:
                engine.dispose()
                raise DBConfigError

            self._engines = engine

    def get_engine(self):
        try:
            return self._engines
        except KeyError:
            raise ConnectionNotFoundError

    def disconnect(self):
        try:
            self._engines.dispose()
            self._engines = None
        except AttributeError:
            raise ConnectionNotFoundError

    def is_connected(self):
        return False if not self._engines else True


conn_manager = DBConnectionManager()
