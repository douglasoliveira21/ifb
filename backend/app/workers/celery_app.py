"""Configuração do Celery para processamento assíncrono."""

from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "ifb",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_default_retry_delay=60,
    task_max_retries=3,
    result_expires=3600,
    # Queues
    task_default_queue="default",
    task_routes={
        "email.*": {"queue": "emails"},
        "tse.*": {"queue": "tse"},
        "camara.*": {"queue": "camara"},
        "senado.*": {"queue": "senado"},
        "news.collect*": {"queue": "news-collect"},
        "news.classify*": {"queue": "news-ai"},
    },
    # Beat schedule
    beat_schedule={
        # Notícias — a cada 2 horas
        "news-collect-batch": {
            "task": "news.collect_all_active_politicians",
            "schedule": crontab(minute=0, hour="*/2"),
        },
        # Câmara — proposições diariamente às 3h
        "camara-sync-propositions-daily": {
            "task": "camara.sync_propositions",
            "schedule": crontab(hour=3, minute=0),
        },
        # Câmara — despesas diariamente às 4h
        "camara-sync-expenses-daily": {
            "task": "camara.sync_expenses",
            "schedule": crontab(hour=4, minute=0),
        },
        # Senado — diariamente às 5h
        "senado-sync-daily": {
            "task": "senado.sync_senators",
            "schedule": crontab(hour=5, minute=0),
        },
    },
)

celery_app.autodiscover_tasks([
    "app.workers",
    "app.integrations.tse",
    "app.integrations.camara",
    "app.integrations.senado",
    "app.integrations.news",
])
