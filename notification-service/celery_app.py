from celery import Celery
from kombu import Queue
import os

RABBIT_URL = os.getenv('RABBIT_URL', 'amqp://guest:guest@localhost')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/1')

celery_app = Celery(
    broker=RABBIT_URL,
    backend=REDIS_URL,
    include=['notification_tasks']
)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content='json',
    timezone='Europe/Moscow',
    enable_utc=True,
    worker_prefetch_multiplier=4,
    task_acks_late=True,
    task_reject_on_worker_lost=True

)

celery_app.conf.task_queues = (
    Queue(
        'notification',
        durable=True,
        queue_arguments={
            'x-max-priority': 10,
            'x-dead-letter-exchange': 'dlx',
            'x-dead-letter-routing-key': 'dead_letters',
            'x-message-ttl': 5 * 60 * 1000
        }
    )
)