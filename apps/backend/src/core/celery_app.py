from celery import Celery

from src.core.config import settings

app = Celery("persv", broker=str(settings.REDIS_URL))

app.autodiscover_tasks(["src.auth", "src.pipeline"])
