import json
from redis.asyncio import Redis


class CacheService:
    TASKS_TTL = 60
    PROFILE_TTL = 300

    def __init__(self, redis: Redis):
        self.redis = redis

    @staticmethod
    def tasks_key(user_id: int) -> str:
        return f'tasks:user:{user_id}'

    @staticmethod
    def profile_key(user_id: int) -> str:
        return f'user:profile:{user_id}'

    async def get_tasks(self, user_id: int) -> list | None:
        cached = await self.redis.get(self.tasks_key(user_id))
        return json.loads(cached) if cached else None

    async def set_tasks(self, user_id: int, tasks: list) -> None:
        #Задачи - Pydantic объекты коверритуем в словари
        serializable = [t.model_dump() if hasattr(t, 'model_dump') else t for t in tasks]
        await self.redis.set(
            self.tasks_key(user_id),
            json.dumps(serializable, default=str),
            self.TASKS_TTL
        )

    async def get_profile(self, user_id: int) -> dict | None:
        cached = await self.redis.get(self.get_profile(user_id))
        return json.loads(cached) if cached else None

    async def set_profile(self, user_id: int, profile: dict) -> None:
        await self.redis.set(
            self.profile_key(user_id),
            json.dumps(profile, default=str),
            self.PROFILE_TTL

        )

    async def check_login_rate_limit(
            self,
            identifier: str,
            max_attempts: int = 5,
            window: int = 60
    ) -> tuple[bool, int]:
        key = f'rate_limit:login:{identifier}'
        count = await self.redis.incr(key)
        if count == 1:
            await self.redis.expire(key, window)
        return count <= max_attempts, count
