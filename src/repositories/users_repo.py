from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, username: str, email: str, hashed_password: str) -> User:
        hashed_password = hashed_password
        user = User(username=username, email=email, hashed_password=hashed_password)
        self.session.add(user)
        await self.session.commit()  # Фиксируем изменения в БД
        await self.session.refresh(user)  # Подтягиваем данные из бд
        return user

    async def get_all_users(self) -> list[User]:
        stmt = select(User).where(User.is_active == True)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def get_user_by_username(self, username: str) -> User:
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def deactivate_user(self, user_id: int) -> User | None:
        user = await self.get_user_by_id(user_id)
        if user:
            user.is_active = False
            await self.session.commit()
            await self.session.refresh(user)
        return user
