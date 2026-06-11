import time
from celery_app import celery_app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@celery_app.task(
    bind=True,
    queue = 'notification',
    autoretry_for = (ConnectionError, ),
    max_retries=3,
    retry_backoff=True
)
def send_email(self, to: str, subject: str, body: str) -> dict:
    logger.info(f'[send_email] attempt = {self.request.retries + 1} -> {to}')
    time.sleep(0.5)
    logger.info(f'[send_email] DONE -> {to}')
    return {'status': 'sent', 'to': to, 'subject': subject, 'body': body}

