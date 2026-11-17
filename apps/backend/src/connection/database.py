import base64
import json
import logging
import os
from datetime import timedelta
from pathlib import Path
from threading import Lock, RLock
from types import MappingProxyType

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from langgraph.graph.state import CompiledStateGraph
from pydantic import ValidationError
from sqlalchemy import Engine, create_engine, make_url, text
from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError

from src.agent.builder import create_sql_agent
from src.connection.config import conn_settings
from src.connection.exceptions import ConnectionNotFoundError, DBConfigError
from src.connection.schemas import (
    CacheEntry,
    ConnectionDetails,
    ConnectionPayload,
    ConnectionRecord,
    ConnectionStatus,
    CustomCacheEntry,
    CustomPayload,
    DemoCacheEntry,
    DemoPayload,
    connection_adapter,
)
from src.connection.utils import LRUCache
from src.core.redis_client import redis_client
from src.core.utils import get_current_datetime, get_internal_db_url

logger = logging.getLogger(__name__)

DEMO_ENGINE = create_engine(
    get_internal_db_url(
        username=conn_settings.PG_DEMO_USER, password=conn_settings.PG_DEMO_PASSWORD
    ),
    pool_pre_ping=True,
    pool_recycle=300,
)
DEMO_AGENT = create_sql_agent(engine=DEMO_ENGINE, schema=conn_settings.PG_DEMO_SCHEMA)


class ConnectionKey:
    PREFIX = "connection"

    @classmethod
    def for_user(cls, user_id: str) -> str:
        return f"{cls.PREFIX}:{user_id}"


class CustomDBConnectionManager:
    def __init__(self) -> None:
        self.__locks_mutex = Lock()  # ensures each user gets a single shared lock
        self.__locks: dict[
            str, RLock
        ] = {}  # per-user locks that serialize cache mutations
        self.__connections: LRUCache[Engine, CompiledStateGraph] = LRUCache(
            capacity=conn_settings.CACHE_CAPACITY
        )

    def connect(
        self,
        user_id: str,
        schema: str | None = None,
        url: URL | None = None,
        db_file_path: str | None = None,
    ) -> None:
        with self.__get_user_lock(user_id=user_id):
            if url:  # CUSTOM
                engine = self.__build_engine(url=url)
                self.__test_connection(engine=engine, db_file_path=db_file_path)

                agent = create_sql_agent(engine=engine, schema=schema)

                parsed = make_url(url)
                self.__commit_connection(
                    user_id=user_id,
                    payload=CustomPayload(
                        db_schema=schema,
                        connected_at=get_current_datetime().isoformat(),
                        connection_details=ConnectionDetails(
                            dbms=parsed.get_backend_name(),
                            encrypted_url=self.__encrypt_connection(url=url),
                            db=parsed.database,
                            db_file_path=db_file_path,
                        ),
                    ),
                    engine=engine,
                    agent=agent,
                    ttl=conn_settings.CONN_EXP,
                )
            else:  # DEMO
                self.__test_connection(DEMO_ENGINE)
                self.__commit_connection(
                    user_id=user_id,
                    payload=DemoPayload(
                        db_schema=schema,
                        connected_at=get_current_datetime().isoformat(),
                    ),
                    ttl=conn_settings.CONN_EXP,
                )

    def disconnect(self, user_id: str) -> None:
        with self.__get_user_lock(user_id=user_id):
            connection = self.get_connection(user_id=user_id)
            if not connection:
                raise ConnectionNotFoundError

            self.clear_cached_connection(user_id=user_id)
            redis_client.delete(ConnectionKey.for_user(user_id=user_id))

    @staticmethod
    def reset_expiry(user_id: str) -> bool:
        return redis_client.expire(
            ConnectionKey.for_user(user_id=user_id), conn_settings.CONN_EXP
        )

    def get_agent(self, user_id: str) -> CompiledStateGraph:
        agent = self.__get_cached_agent(user_id=user_id)
        if not agent:
            connection = self.get_connection(user_id=user_id)
            if not connection:  # Not connected
                raise ConnectionNotFoundError
            if isinstance(connection, DemoPayload):  # Connected to demo
                # Since Demo cache entry's format is consistent, no lock is needed
                agent = DEMO_AGENT
                self.__cache_connection(user_id=user_id, cache_entry=DemoCacheEntry())
            else:  # Connected to a custom database
                with self.__get_user_lock(
                    user_id=user_id
                ):  # Another thread may have populated the cache while we waited.
                    agent = self.__get_cached_agent(user_id)
                    if not agent:
                        encrypted_url = connection.connection_details.encrypted_url
                        conn_url = self.__decrypt_connection(encrypted=encrypted_url)

                        engine = self.__build_engine(url=conn_url)
                        schema = self.get_schema(user_id=user_id)
                        agent = create_sql_agent(engine=engine, schema=schema)

                        db_file_path = connection.connection_details.db_file_path

                        self.__cache_connection(
                            user_id=user_id,
                            cache_entry=CustomCacheEntry(
                                engine=engine, agent=agent, db_file_path=db_file_path
                            ),
                        )

        return agent

    def get_schema(self, user_id: str | None) -> str | None:
        if not user_id:
            return conn_settings.PG_DEMO_SCHEMA

        record = self.get_connection(user_id)
        if not record:
            raise ConnectionNotFoundError
        return record.db_schema

    @staticmethod
    def get_connection(user_id: str) -> ConnectionRecord | None:
        raw = redis_client.get(ConnectionKey.for_user(user_id=user_id))
        if not raw:
            return None

        try:
            payload = connection_adapter.validate_json(raw)
            # Check if file still exists in the system when connecting to SQLite database
            if isinstance(payload, CustomPayload):
                file_path = payload.connection_details.db_file_path

                if file_path:
                    path = Path(file_path)
                    if not path.is_file():
                        return None

            return payload
        except ValidationError:
            return None

    def get_connection_status(self, user_id: str | None) -> ConnectionStatus:
        if not user_id:
            return ConnectionStatus(connected=False)

        connection = self.get_connection(user_id=user_id)
        if not connection:
            return ConnectionStatus(connected=False)

        db = (
            connection.connection_details.db
            if isinstance(connection, CustomPayload)
            else "demo"
        )
        return ConnectionStatus(connected=True, database=db)

    @staticmethod
    def __test_connection(engine: Engine, db_file_path: str | None = None) -> None:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except SQLAlchemyError as e:
            engine.dispose()
            if db_file_path:
                Path(db_file_path).unlink(missing_ok=True)
            logger.warning(e)
            raise DBConfigError

    def __commit_connection(
        self,
        user_id: str,
        payload: ConnectionPayload,
        engine: Engine | None = None,
        agent: CompiledStateGraph | None = None,
        ttl: timedelta | None = None,
    ) -> None:
        self.clear_cached_connection(user_id=user_id)

        serialized = json.dumps(payload.model_dump_json())
        redis_client.setex(ConnectionKey.for_user(user_id=user_id), ttl, serialized)

        if isinstance(payload, CustomPayload) and engine and agent:  # CUSTOM
            self.__cache_connection(
                user_id=user_id,
                cache_entry=CustomCacheEntry(
                    engine=engine,
                    agent=agent,
                    db_file_path=payload.connection_details.db_file_path,
                ),
            )
        else:  # DEMO
            self.__cache_connection(user_id=user_id, cache_entry=DemoCacheEntry())

    @staticmethod
    def __release(entry: CacheEntry | None) -> None:
        if not isinstance(entry, CustomCacheEntry):
            return
        entry.engine.dispose()
        if entry.db_file_path:
            Path(entry.db_file_path).unlink(missing_ok=True)
        # agent needs no explicit cleanup since it doesn't hold an OS-level resource
        # (socket, file handle, thread) that needs manual teardown

    def __cache_connection(self, user_id: str, cache_entry: CacheEntry) -> None:
        for evicted in self.__connections.put(user_id, cache_entry):
            self.__release(evicted)

    def clear_cached_connection(self, user_id: str) -> None:
        hit = self.__connections.pop(user_id)
        self.__release(hit)

    @staticmethod
    def __build_engine(url: URL | str) -> Engine:
        return create_engine(
            url,
            pool_size=1,
            max_overflow=0,
            pool_pre_ping=True,
            pool_timeout=30,
            pool_recycle=3600,
        )

    def __get_cached_agent(self, user_id: str) -> CompiledStateGraph | None:
        hit = self.__connections.get(user_id)
        if not hit:
            return None
        return DEMO_AGENT if isinstance(hit, DemoCacheEntry) else hit.agent

    def get_cache(self) -> MappingProxyType:
        return self.__connections.get_cache()

    def __get_user_lock(self, user_id: str) -> RLock:
        with self.__locks_mutex:
            if user_id not in self.__locks:
                self.__locks[user_id] = RLock()
            return self.__locks[user_id]

    def clear_user_lock(self, user_id: str) -> None:
        with self.__locks_mutex:
            self.__locks.pop(user_id, None)

    @staticmethod
    def __encrypt_connection(url: URL | str) -> str:
        """Encrypt a connection string using AES-256-GCM.

        Args:
            url: The raw database connection URL to encrypt.

        Returns:
            A base64-encoded string containing the nonce and ciphertext.
        """
        key = base64.b64decode(conn_settings.ENCRYPTION_KEY)
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)  # 96-bit nonce, required for GCM

        plain_url = (
            url.render_as_string(hide_password=False) if isinstance(url, URL) else url
        )

        ciphertext = aesgcm.encrypt(nonce, plain_url.encode(), None)
        # prepend nonce to ciphertext so we can recover it during decryption
        return base64.b64encode(nonce + ciphertext).decode()

    @staticmethod
    def __decrypt_connection(encrypted: str) -> str:
        """Decrypt a connection string encrypted with AES-256-GCM.

        Args:
            encrypted: A base64-encoded string containing the nonce and ciphertext.

        Returns:
            The original plaintext connection URL.
        """
        key = base64.b64decode(conn_settings.ENCRYPTION_KEY)
        aesgcm = AESGCM(key)
        data = base64.b64decode(encrypted)
        nonce = data[:12]
        ciphertext = data[12:]
        return aesgcm.decrypt(nonce, ciphertext, None).decode()


custom_conn_manager = CustomDBConnectionManager()
