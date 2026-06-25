from fastapi import FastAPI
from src.database import engine, Base, client as mongo_client
from src.routers import tasks, users, auth_router, note, weather
from contextlib import asynccontextmanager
from redis_client import redis_client
import sentry_sdk

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await redis_client.ping()
    yield
    await engine.dispose()
    mongo_client.close()
    await redis_client.close()


sentry_sdk.init(
    dsn="https://92b0a6fa51698f633f426f8855810a02@o4511569252450304.ingest.de.sentry.io/4511570852118608",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)

app = FastAPI(
    title="FastAPI Tracker API",
    description="A simple API to track and manage items.",
    version="1.0.0",
    # lifespan=lifespan
)




app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(auth_router.router)
app.include_router(note.router)
app.include_router(weather.router)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI Tracker API!"}


@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)