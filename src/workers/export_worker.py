import asyncio
import json
import csv
import io
import os
from pathlib import Path
import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from src.database import async_session_maker
from src.rabbitmq import get_rabbit_connection, Queues
from src.repositories.tasks_repo import TaskRepository


EXPORT_DIR = Path('exports')


async def handle_export(message: AbstractIncomingMessage):
    async with message.process(requeue=True):
        payload = json.loads(message.body.decode())
        user_id = payload['user_id']
        fmt = payload.get('fmt', 'csv')

        async with async_session_maker() as session:
            repo = TaskRepository(session)
            tasks = await repo.get_all_tasks_for_user(user_id)

        print(f'export: Начинаю экспортировать')

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['id', 'title', 'priority', 'is_done', 'created_at'])

        for task in tasks:
            writer.writerow([
                task.id, task.title,
                task.priority, task.is_done,
                task.created_at
            ])

            filename = EXPORT_DIR / f'user_{user_id}_tasks.{fmt}'
            filename.write_text(output.getvalue(), encoding='utf-8')


async def main():
    conn = await get_rabbit_connection()

    channel = conn.channel()
    await channel.set_qos(prefetch_count=1)
    queue = await channel.declare_queue(Queues.TASK_EXPORT, durable=True)
    async with queue.iterator() as q:
        async for message in q:
            await handle_export(message)
    await channel.close()


if __name__ == '__main__':
    asyncio.run(main())





