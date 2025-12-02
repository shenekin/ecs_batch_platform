
from celery import Celery
from app.core.config import settings

celery = Celery('ecs_batch', broker=settings.CELERY_BROKER, backend=settings.CELERY_BACKEND)
celery.conf.task_acks_late = True
celery.conf.worker_prefetch_multiplier = 1
