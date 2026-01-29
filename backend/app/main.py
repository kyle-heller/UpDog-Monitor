import secrets
from contextlib import asynccontextmanager
from app.api.monitors import router as monitors_router
from app.api.health import router as health_router
from app.api.slo import router as slo_router
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import text
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.worker.checker import run_checks
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.middleware.cors import CORSMiddleware
from app.core.db import engine
from app.core.config import settings

security = HTTPBasic()


def verify_metrics_auth(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify basic auth for /metrics endpoint."""
    if not settings.metrics_password:
        # No password set = no auth required
        return True

    correct_username = secrets.compare_digest(
        credentials.username.encode("utf8"),
        settings.metrics_username.encode("utf8"),
    )
    correct_password = secrets.compare_digest(
        credentials.password.encode("utf8"),
        settings.metrics_password.encode("utf8"),
    )

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True


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
    version="0.8.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://valiant-amazement-production-5a84.up.railway.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(monitors_router, prefix="/api")
app.include_router(health_router, prefix="/api")
app.include_router(slo_router, prefix="/api")

Instrumentator().instrument(app).expose(
    app, dependencies=[Depends(verify_metrics_auth)]
)


@app.get("/")
async def root():
    return {"message": "What's updog?"}
