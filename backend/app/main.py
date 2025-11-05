from contextlib import asynccontextmanager
from app.api.monitors import router as monitors_router
from app.api.health import router as health_router
from fastapi import FastAPI
from sqlalchemy import text
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.worker.checker import run_checks

from app.core.db import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: test database connection
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    print("Database connected!")

    # Start the background scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_checks, "interval", seconds=60, id="url_checker")
    scheduler.start()
    print("Scheduler started - checking URLs every 60 seconds")

    yield

    # Shutdown: stop scheduler
    scheduler.shutdown()
    print("Shutting down...")


app = FastAPI(
    title="UpDog Monitor",
    description="URL uptime monitoring service",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(monitors_router, prefix="/api")
app.include_router(health_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "What's updog?"}
