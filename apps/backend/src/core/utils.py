from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from src.core.config import settings


def get_current_datetime() -> datetime:
    return datetime.now(timezone.utc)


def read_text_file(file_path: str | Path) -> str:
    return Path(file_path).read_text(encoding="utf-8")


def get_sqlalchemy_url(
    username: str,
    password: str,
    host: str = settings.PG_HOST,
    port: int = settings.PG_PORT,
    db: str = settings.PG_DATABASE,
    ssl_mode: str | None = settings.PG_SSL_MODE,
    channel_binding: str | None = settings.PG_CHANNEL_BINDING,
) -> str:
    url = f"postgresql+psycopg://{username}:{password}@{host}:{port}/{db}"
    params = []
    if ssl_mode:
        params.append(f"sslmode={ssl_mode}")

    if channel_binding:
        params.append(f"channel_binding={channel_binding}")

    if params:
        url += f"?{'&'.join(params)}"

    return url


def get_redis_url(
    host: str = settings.REDIS_HOST,
    port: int = settings.REDIS_PORT,
    username: str | None = settings.REDIS_USERNAME,
    password: str = settings.REDIS_PASSWORD,
    db: int = 0,
    use_tls: bool = False,
) -> str:
    """Builds a Redis connection URL from individual components.

    Args:
        host: Redis server hostname or IP.
        port: Redis server port.
        username: Optional username for Redis ACL auth.
        password: Optional password for Redis auth.
        db: Redis logical database index.
        use_tls: Whether to use the `rediss://` (TLS) scheme instead of `redis://`.

    Returns:
        A fully formed Redis connection URL.
    """
    scheme = "rediss" if use_tls else "redis"

    auth = ""
    if username and password:
        auth = f"{quote(username)}:{quote(password)}@"
    elif password:
        auth = f":{quote(password)}@"

    return f"{scheme}://{auth}{host}:{port}/{db}"
