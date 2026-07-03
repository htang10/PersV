from celery import Celery
from src.config import settings

app = Celery(
    "persv",
    broker=str(settings.REDIS_URL),
    backend=str(settings.REDIS_URL),
)

app.autodiscover_tasks(["src.auth", "src.pipeline"])
