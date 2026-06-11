import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection


POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "pass")
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE", "python_postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
)

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL)


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
