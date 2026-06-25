import os
import aio_pika
from aio_pika.abc import AbstractRobustConnection

RABBIT_URL = os.getenv('RABBIT_URL', 'amqp://guest:guest@localhost')


class Queues:
    TASK_EXPORT = 'tracker.task.export'
    TASK_NOTIFY = 'tracker.task.notify'
    TASK_REPORT = 'tracker.task.report'


_connection: AbstractRobustConnection | None = None


async def get_rabbit_connection() -> AbstractRobustConnection:
    global _connection
    if _connection is None or _connection.closed:
        _connection = await aio_pika.connect_robust(RABBIT_URL)
    return _connection


async def close_rabbit_connection() -> None:
    global _connection
    if _connection and not _connection.closed:
        await _connection.close()


