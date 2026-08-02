import asyncio
import logging
import math
from itertools import islice

from src.core.redis import redis_client
from src.pipeline.database import custom_conn_manager

logger = logging.getLogger(__name__)
THRESHOLD = 0.3
PERIOD = 30 * 60


async def sweep_stale_connections() -> None:
    while True:
        await asyncio.sleep(PERIOD)
        try:
            logger.info("Cleaning up stale connections...")
            cache = custom_conn_manager.get_cache()
            logger.info(f"Before cleanup: {len(cache)} entries.")
            sample = list(islice(cache.keys(), math.ceil(len(cache) * THRESHOLD)))
            if sample:
                keys = [f"connection:{user_id}" for user_id in sample]
                results = redis_client.mget(keys)
                for user_id, result in zip(sample, results):
                    if not result:
                        custom_conn_manager.clear_cached_engine(user_id=user_id)
            logger.info(
                f"After cleanup: {len(custom_conn_manager.get_cache())} entries."
            )
            logger.info("Finished.")
        except TypeError as e:
            logger.exception(f"Connection cleanup job failed to execute: {e}")
