from fastapi import FastAPI
from src.routers import tasks
from src.routers import users
from src.routers import auth_router

app = FastAPI(
    title="FastAPI Tracker API",
    description="A simple API to track and manage items.",
    version="1.0.0",
)

app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(auth_router.router)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI Tracker API!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)