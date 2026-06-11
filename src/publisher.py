import json
import aio_pika
from src.rabbitmq import get_rabbit_connection, Queues


async def publish(queue_name: str, payload: dict) -> None:
    conn = await get_rabbit_connection()

    channel = await conn.channel()
    await channel.declare_queue(queue_name, durable=True)

    await channel.default_exchange.publish(
        aio_pika.Message(
            body=json.dumps(payload).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type='application/json'
        ), routing_key=queue_name
    )
    await channel.close() #Закрывает канал а не соеденение


async def publish_export_task(user_id: int, fmt: str = 'csv') -> None:
    await publish(Queues.TASK_EXPORT, {
        'user_id': user_id,
        'fmt': fmt
    })


async def publish_notify_task(
        user_id: int,
        email: str,
        task_title: str,
        event: str
) -> None:
    await publish(Queues.TASK_NOTIFY, {
        'user_id': user_id,
        'email': email,
        'task_title': task_title,
        'event': event
    })
