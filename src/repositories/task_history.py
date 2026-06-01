from datetime import  datetime, timezone
from motor.motor_asyncio import AsyncIOMotorCollection

class TaskHistory:
    """
    История изменений задач в MongoDB
    task_id и user_id - ЭТО PG_IDS From  (мост между БД)
    """
    def __init__(self, col: AsyncIOMotorCollection):
        self.col = col

    async def log_cretated(self, task_id: int, user_id: int, snapshot: dict):
        await self.col.insert_one({
            'task_id': task_id,
            'user_id': user_id,
            'event': 'created',
            'snapshot': snapshot,
            'timestamp': datetime.now(timezone.utc)
        })

    async def log_updated(self, task_id: int, user_id: int, changes: dict):
        if not changes:
            return
        await self.col.insert_one({
            'task_id': task_id,
            'user_id': user_id,
            'event': 'updated',
            'changes': changes,
            'timestamp': datetime.now(timezone.utc)
        })

    async def log_deleted(self, task_id: int, user_id: int):
        await self.col.insert_one({
            'task_id': task_id,
            'user_id': user_id,
            'event': 'deleted',
            'timestamp': datetime.now(timezone.utc)
        })

    async def get_task_history(self, task_id: int, limit: int = 50):
        cursor = (
            self.col.find({'task_id': task_id}).sort('timestamp', -1).limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        for doc in docs:
            doc['_id'] = str(doc['_id'])
        return docs

    async def get_last_events(self, tasks_ids: list[int]) -> dict[int, str]:
        if not tasks_ids:
            return {}
        pipeline = [
            {'$match': {'task_id': {'$in': tasks_ids}}},
            {'$sort': {'timestamp', -1}},
            {'$group': {'_id': '$task_id',
                        'last_event': {'$first': '$event'}}}
        ]
        docs = await self.col.aggregate(pipeline).to_list(length=len(tasks_ids))
        return {doc['_id']: doc['last_event'] for doc in docs}