import base64
import json
import logging
import os
from threading import Lock, RLock
from types import MappingProxyType

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from langgraph.graph.state import CompiledStateGraph
from sqlalchemy import Engine, create_engine, make_url, text
from sqlalchemy.exc import SQLAlchemyError

from src.core.redis import redis_client
from src.core.utils import get_current_datetime
from src.pipeline.agent.builder import create_sql_agent
from src.pipeline.config import pl_settings
from src.pipeline.exceptions import ConnectionNotFoundError, DBConfigError
from src.pipeline.schemas import ConnectionStatus
from src.pipeline.utils import LRUCache

logger = logging.getLogger(__name__)

DEMO_ENGINE = create_engine(str(pl_settings.DEMO_DB_URL))
DEMO_AGENT = create_sql_agent(engine=DEMO_ENGINE, schema=pl_settings.DEMO_SCHEMA)


class CustomDBConnectionManager:
    def __init__(self) -> None:
        self.__locks_mutex = Lock()  # protects locks
        self.__locks: dict[str, RLock] = {}  # protects engines
        self.__connections: LRUCache[Engine, CompiledStateGraph] = LRUCache(
            capacity=pl_settings.CACHE_CAPACITY
        )

    def connect(
        self,
        user_id: str,
        schema: str,
        url: str | None = None,
    ) -> None:
        with self.__get_user_lock(user_id=user_id):
            if url:  # CUSTOM
                engine = self.__build_engine(url=url)
                self.__test_connection(engine=engine)

                agent = create_sql_agent(engine=engine, schema=schema)

                parsed = make_url(url)
                self.__commit_connection(
                    user_id=user_id,
                    payload={
                        "target": "custom",
                        "dbms": parsed.get_backend_name(),
                        "url": self.__encrypt_connection(url=url),
                        "db": parsed.database,
                        "schema": schema,
                        "connected_at": get_current_datetime().isoformat(),
                    },
                    engine=engine,
                    agent=agent,
                    ttl=pl_settings.CONN_EXP,
                )
            else:  # DEMO
                self.__test_connection(DEMO_ENGINE)
                self.__commit_connection(
                    user_id=user_id,
                    payload={
                        "target": "demo",
                        "connected_at": get_current_datetime().isoformat(),
                        "schema": schema,
                    },
                )

    def disconnect(self, user_id: str) -> None:
        with self.__get_user_lock(user_id=user_id):
            connection = self.get_connection(user_id=user_id)
            if not connection:
                raise ConnectionNotFoundError

            self.clear_cached_connection(user_id=user_id)
            redis_client.delete(f"connection:{user_id}")

    @staticmethod
    def reset_expiry(user_id: str) -> bool:
        return redis_client.expire(f"connection:{user_id}", pl_settings.CONN_EXP)

    def get_agent(self, user_id: str | None = None) -> CompiledStateGraph:
        if not user_id:  # GUESTS
            agent = DEMO_AGENT
        else:  # USERS
            agent = self.__get_cached_agent(user_id=user_id)
            if not agent:
                record = self.get_connection(user_id)
                if not record:  # Not connected
                    raise ConnectionNotFoundError
                if record["target"] == "demo":  # Connected to demo
                    agent = DEMO_AGENT
                    self.__cache_connection(
                        user_id=user_id, target="demo", engine=None, agent=None
                    )
                else:  # Connected to a custom database
                    with self.__get_user_lock(
                        user_id=user_id
                    ):  # Another thread may have populated the cache while we waited.
                        agent = self.__get_cached_agent(user_id)
                        if not agent:
                            encrypted_url = record["url"]
                            recorded_url = self.__decrypt_connection(
                                encrypted=encrypted_url
                            )
                            engine = self.__build_engine(url=recorded_url)

                            agent = create_sql_agent(
                                engine=engine, schema=self.get_schema(user_id=user_id)
                            )

                            self.__cache_connection(
                                user_id=user_id,
                                target="custom",
                                engine=engine,
                                agent=agent,
                            )

        return agent

    def get_schema(self, user_id: str | None) -> str:
        if not user_id:
            return pl_settings.DEMO_SCHEMA

        record = self.get_connection(user_id)
        if not record:
            raise ConnectionNotFoundError
        return record["schema"]

    @staticmethod
    def get_connection(user_id: str) -> dict | None:
        raw = redis_client.get(f"connection:{user_id}")
        if not raw:
            return None
        return json.loads(raw)

    def get_connection_status(self, user_id: str) -> ConnectionStatus:
        connection = self.get_connection(user_id=user_id)
        if not connection:
            return ConnectionStatus(connected=False)
        db = connection["db"] if connection["target"] == "custom" else "demo"
        return ConnectionStatus(connected=True, database=db)

    @staticmethod
    def __test_connection(engine: Engine) -> None:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except SQLAlchemyError as e:
            engine.dispose()
            logger.error(e)
            raise DBConfigError

    def __commit_connection(
        self,
        user_id: str,
        payload: dict,
        engine: Engine | None = None,
        agent: CompiledStateGraph | None = None,
        ttl: int | None = None,
    ) -> None:
        status = self.get_connection_status(user_id=user_id)
        if status.connected:
            self.disconnect(user_id)

        serialized = json.dumps(payload)
        if engine and agent and ttl:  # CUSTOM
            redis_client.setex(f"connection:{user_id}", ttl, serialized)
            self.__cache_connection(
                user_id=user_id, target="custom", engine=engine, agent=agent
            )
        else:  # DEMO
            redis_client.set(f"connection:{user_id}", serialized)
            self.__cache_connection(
                user_id=user_id, target="demo", engine=None, agent=None
            )

    def __cache_connection(
        self,
        user_id: str,
        target: str,
        engine: Engine | None,
        agent: CompiledStateGraph | None,
    ) -> None:
        evicted = self.__connections.put(user_id, target, engine, agent)
        if evicted and evicted["target"] == "custom":
            engine = evicted["engine"]
            assert engine is not None
            engine.dispose()
            # agent needs no explicit cleanup since it doesn't hold an OS-level resource
            # (socket, file handle, thread) that needs manual teardown

    def clear_cached_connection(self, user_id: str) -> None:
        hit = self.__connections.pop(user_id)
        if hit and hit["target"] == "custom":
            engine = hit["engine"]
            assert engine is not None
            engine.dispose()
            # agent needs no explicit cleanup since it doesn't hold an OS-level resource
            # (socket, file handle, thread) that needs manual teardown

    @staticmethod
    def __build_engine(url: str) -> Engine:
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
        return DEMO_AGENT if hit["target"] == "demo" else hit["agent"]

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
    def __encrypt_connection(url: str) -> str:
        """Encrypt a connection string using AES-256-GCM.

        Args:
            url: The raw database connection URL to encrypt.

        Returns:
            A base64-encoded string containing the nonce and ciphertext.
        """
        key = base64.b64decode(pl_settings.ENCRYPTION_KEY)
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)  # 96-bit nonce, required for GCM
        ciphertext = aesgcm.encrypt(nonce, url.encode(), None)
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
        key = base64.b64decode(pl_settings.ENCRYPTION_KEY)
        aesgcm = AESGCM(key)
        data = base64.b64decode(encrypted)
        nonce = data[:12]
        ciphertext = data[12:]
        return aesgcm.decrypt(nonce, ciphertext, None).decode()


custom_conn_manager = CustomDBConnectionManager()
