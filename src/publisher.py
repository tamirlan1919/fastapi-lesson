import json
import asyncio
from src.celery_app import celery_app


async def publish_notify_task(
        user_id: int,
        email: str,
        task_title: str,
        event: str
) -> None:
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: celery_app.send_task(
            'notification.tasks.send_email',
            kwargs={
                'user_id': user_id,
                'to': email,
                'subject': f'Задача [{event}]: {task_title}',
                'body': 'notification',
            },
            queue='notification'
        )
    )
    return result.id


async def publish_report_task(user_id: int, task_data: list[dict]) -> str:
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: celery_app.send_task(
            'reports.tasks.generate_csv_report',
            kwargs={
                'user_id': user_id,
                'task_data': task_data,
            },
            queue='reports'
        )
    )
    return result.id
