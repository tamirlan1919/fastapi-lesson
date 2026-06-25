import csv
import io
import os
from pathlib import Path
from celery_app import celery_app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)
EXPORT_DIR = Path(os.getenv('EXPORT_DIR', '/tmp_dir'))

@celery_app.task(
    bind=True,
    name='reports.tasks.generate_csv_report',
    queue='reports',
    max_retries=3,
    autoretry_for = (Exception, ),
    retry_backoff = True,
    time_limit = 300,
    soft_time_limit = 200
)
def generate_csv_report(self, user_id: int, task_data: list) -> dict:
    from celery.exceptions import  SoftTimeLimitExceeded
    logger.info(f'[{self.request.id}] старт user_id={user_id} задач - {len(task_data)}')
    try:
        self.update_state(state='PROGRESS', meta={'current': 0, 'total': len(task_data)})
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['id', 'title', 'priority', 'is_done', 'created_at', 'deadline'])
        for i, task in enumerate(task_data):
            writer.writerow([
                task.get('id'), task.get('title'), task.get('priority'),
                task.get('is_done'), task.get('created_at'),
                task.get('deadline', '')
            ])
            if i % 10 == 0:
                self.update_state(state='PROGRESS', meta = {'current': i, 'total': len(task_data)})
        EXPORT_DIR.mkdir(exist_ok=True)
        filename = EXPORT_DIR / f'user_{user_id}_tasks.csv'
        filename.write_text(output.getvalue(), encoding='utf-8')
    except SoftTimeLimitExceeded:
        logger.warning(f'[{self.request.id}] timeout for user_id - {user_id}', exc_info=True)
        raise
