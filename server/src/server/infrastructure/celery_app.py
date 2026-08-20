"""PullSense Server — Infrastructure: Celery application configuration."""

from __future__ import annotations

from celery import Celery

from server.config import get_settings

settings = get_settings()

celery_app = Celery(
    "pullsense",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Task execution
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
    # Result expiration (1 hour)
    result_expires=3600,
    # Task routing
    task_routes={
        "server.workers.review_tasks.*": {"queue": "reviews"},
        "server.workers.sync_tasks.*": {"queue": "sync"},
        "server.workers.cleanup_tasks.*": {"queue": "cleanup"},
    },
    # Default queue
    task_default_queue="default",
    # Retry defaults
    task_default_retry_delay=30,
    task_max_retries=3,
)

# Auto-discover tasks in the workers package
celery_app.autodiscover_tasks(["server.workers"])
