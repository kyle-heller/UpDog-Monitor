# [APScheduler + httpx + SQLAlchemy] - Background URL checker
import asyncio
from datetime import datetime

import httpx
from sqlalchemy import select

from app.core.db import async_session
from app.models.monitor import Monitor
from app.models.result import CheckResult


async def check_url(monitor: Monitor) -> CheckResult:
    """Check a single URL and return the result."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            start = datetime.utcnow()
            response = await client.get(str(monitor.url))
            elapsed_ms = int((datetime.utcnow() - start).total_seconds() * 1000)

            return CheckResult(
                monitor_id=monitor.id,
                status_code=response.status_code,
                response_time_ms=elapsed_ms,
                is_up=response.status_code < 400,
                checked_at=datetime.utcnow(),
            )
        except Exception as e:
            return CheckResult(
                monitor_id=monitor.id,
                status_code=None,
                response_time_ms=None,
                is_up=False,
                checked_at=datetime.utcnow(),
                error_message=str(e),
            )


async def run_checks():
    """Load all active monitors and check them."""
    async with async_session() as db:
        # Get all active monitors
        result = await db.execute(select(Monitor).where(Monitor.is_active == True))
        monitors = result.scalars().all()

        if not monitors:
            print("No active monitors to check")
            return

        print(f"Checking {len(monitors)} monitors...")

        # Check all URLs concurrently
        tasks = [check_url(monitor) for monitor in monitors]
        results = await asyncio.gather(*tasks)

        # Save all results
        for check_result in results:
            db.add(check_result)

        await db.commit()
        print(f"Saved {len(results)} check results")
