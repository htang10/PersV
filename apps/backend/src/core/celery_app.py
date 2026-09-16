from celery import Celery

from src.core.utils import get_redis_url

app = Celery("persv", broker=get_redis_url())

app.autodiscover_tasks(["src.auth", "src.pipeline"])
