import base64
import json
import logging
import os
from threading import Lock, RLock
from types import MappingProxyType

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from sqlalchemy import Engine, create_engine, make_url, text
from sqlalchemy.exc import SQLAlchemyError

from core.redis import redis_client
from core.utils import get_current_datetime
from pipeline.schemas import ConnectionStatus
from pipeline.utils import LRUEngineCache
from src.pipeline.config import pl_settings
from src.pipeline.exceptions import ConnectionNotFoundError, DBConfigError

logger = logging.getLogger(__name__)

DEMO_ENGINE = create_engine(str(pl_settings.DEMO_DB_URL))


class CustomDBConnectionManager:
    MAX_ENGINES = 100

    def __init__(self) -> None:
        self.__locks_mutex = Lock()  # protects locks
        self.__locks: dict[str, RLock] = {}  # protects engines
        self.__engines = LRUEngineCache(capacity=self.__class__.MAX_ENGINES)

    def connect(
        self, user_id: str, url: str | None = None, schema: str | None = None
    ) -> None:
        with self.__get_user_lock(user_id=user_id):
            if url:  # CUSTOM
                engine = self.__build_engine(url=url)
                self.__test_connection(engine=engine)

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
                    ttl=pl_settings.CONN_EXP,
                )
            else:  # DEMO
                self.__test_connection(DEMO_ENGINE)
                self.__commit_connection(
                    user_id=user_id,
                    payload={
                        "target": "demo",
                        "connected_at": get_current_datetime().isoformat(),
                    },
                )

    def disconnect(self, user_id: str) -> None:
        with self.__get_user_lock(user_id=user_id):
            connection = self.get_connection(user_id=user_id)
            if not connection:
                logger.error("Failed due to invalid user id.")
                raise ConnectionNotFoundError

            self.clear_cached_engine(user_id=user_id)
            redis_client.delete(f"connection:{user_id}")

    @staticmethod
    def reset_expiry(user_id: str) -> bool:
        return redis_client.expire(f"connection:{user_id}", pl_settings.CONN_EXP)

    def get_engine(self, user_id: str | None = None) -> Engine:
        if not user_id:  # GUESTS
            engine = DEMO_ENGINE
        else:  # USERS
            engine = self.__get_cached_engine(user_id=user_id)
            if not engine:
                record = self.get_connection(user_id)
                if not record:  # Not connected
                    raise ConnectionNotFoundError
                if record["target"] == "demo":  # Connected to demo
                    engine = DEMO_ENGINE
                    self.__cache_engine(user_id=user_id, target="demo")
                else:  # Connected to a custom database
                    with self.__get_user_lock(
                        user_id=user_id
                    ):  # Another thread may have populated the cache while we waited.
                        engine = self.__get_cached_engine(user_id)
                        if not engine:
                            encrypted_url = record["url"]
                            recorded_url = self.__decrypt_connection(
                                encrypted=encrypted_url
                            )
                            engine = self.__build_engine(url=recorded_url)
                            self.__cache_engine(
                                user_id=user_id, target="custom", engine=engine
                            )

        return engine

    def get_schema(self, user_id: str) -> str | None:
        record = self.get_connection(user_id)
        if not record:
            return None
        return record["schema"] if record["target"] == "custom" else None

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
        ttl: int | None = None,
    ) -> None:
        status = self.get_connection_status(user_id=user_id)
        if status.connected:
            self.disconnect(user_id)

        serialized = json.dumps(payload)
        if ttl and engine:
            redis_client.setex(f"connection:{user_id}", ttl, serialized)
            self.__cache_engine(user_id=user_id, target="custom", engine=engine)
        else:
            redis_client.set(f"connection:{user_id}", serialized)
            self.__cache_engine(user_id=user_id, target="demo")

    def __get_user_lock(self, user_id: str) -> RLock:
        with self.__locks_mutex:
            if user_id not in self.__locks:
                self.__locks[user_id] = RLock()
            return self.__locks[user_id]

    def clear_user_lock(self, user_id: str) -> None:
        with self.__locks_mutex:
            self.__locks.pop(user_id, None)

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

    def __cache_engine(
        self, user_id: str, target: str, engine: Engine | None = None
    ) -> None:
        self.__engines.put(user_id, target, engine)

    def __get_cached_engine(self, user_id: str) -> Engine | None:
        hit = self.__engines.get(user_id)
        if not hit:
            return None
        return DEMO_ENGINE if hit["target"] == "demo" else hit["engine"]

    def clear_cached_engine(self, user_id: str) -> None:
        hit = self.__engines.pop(user_id)
        if hit and hit["target"] == "custom":
            hit["engine"].dispose()

    def get_cache(self) -> MappingProxyType[str, Engine]:
        return self.__engines.get_cache()

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
