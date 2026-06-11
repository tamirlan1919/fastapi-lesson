from fastapi import FastAPI

from src.database import engine, Base, client as mongo_client
from src.routers import tasks
from src.routers import users
from src.routers import auth_router
from src.routers import note
from contextlib import asynccontextmanager
from redis_client import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await redis_client.ping()
    yield
    await engine.dispose()
    mongo_client.close()
    await redis_client.close()



app = FastAPI(
    title="FastAPI Tracker API",
    description="A simple API to track and manage items.",
    version="1.0.0",
    lifespan=lifespan
)




app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(auth_router.router)
app.include_router(note.router)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI Tracker API!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)