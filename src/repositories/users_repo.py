from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from src.models import User
from fastapi import HTTPException, status


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, username: str, email: str, hashed_password: str) -> User:
        try:
            user = User(username=username, email=email, hashed_password=hashed_password)
            self.session.add(user)
            await self.session.flush()
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Ошибка создания пользователя'
            )
        await self.session.refresh(user)
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
        if not user:
            return None
        try:
            user.is_active = False
            await self.session.flush()
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=500,
                detail='Ошибка деактивации пользователя'
            )
        await self.session.refresh(user)
        return user
