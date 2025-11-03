from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.core.db import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: test database connection
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    print("Database connected!")
    yield
    # Shutdown: cleanup (nothing for now)
    print("Shutting down...")


app = FastAPI(
    title="UpDog Monitor",
    description="URL uptime monitoring service",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {"message": "What's updog?"}
