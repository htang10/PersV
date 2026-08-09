import logging

from redis.exceptions import ConnectionError
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.auth.dependencies import AUTH_ENGINE
from src.core.redis import redis_client
from src.core.schemas import HealthStatus
from src.pipeline.database import DEMO_ENGINE

logger = logging.getLogger(__name__)


def check_database() -> bool:
    logger.info("Checking database...")
    with Session(AUTH_ENGINE) as session:
        if not session.execute(select(1)):
            return False

    with Session(DEMO_ENGINE) as session:
        if not session.execute(select(1)):
            return False

    return True


def check_redis() -> bool:
    logger.info("Checking redis...")
    try:
        return redis_client.ping()
    except ConnectionError as e:
        logger.error(e)
        return False


def check_health() -> HealthStatus:
    db_check = check_database()
    redis_check = check_redis()
    if db_check and redis_check:
        logger.info(
            {
                "status": "healthy",
                "services": {
                    "postgresql": "healthy",
                    "redis": "healthy",
                },
            }
        )
        return HealthStatus(status="healthy")

    health_log = {"status": "unhealthy", "services": {}}

    db_status = "healthy" if db_check else "unhealthy"
    health_log["services"]["postgresql"] = db_status

    redis_status = "healthy" if redis_check else "unhealthy"
    health_log["services"]["redis"] = redis_status

    logger.info(health_log)

    return HealthStatus(status="unhealthy")
