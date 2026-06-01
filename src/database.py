from pathlib import Path

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection


BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR / 'lesson.db'}"

client = AsyncIOMotorClient('mongodb://localhost:27017')


engine = create_async_engine(
    url=DATABASE_URL,
    echo=True
)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


def get_task_history_collection() -> AsyncIOMotorCollection:
    return client['mongo_test']['task_history']


def get_notes_collection() -> AsyncIOMotorCollection:
    return client['mongo_test']['notes']


async def get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


class Base(DeclarativeBase):
    pass

