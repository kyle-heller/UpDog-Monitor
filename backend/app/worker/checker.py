# [APScheduler + httpx + SQLAlchemy] - Background URL checker
import asyncio
from datetime import datetime

import httpx
from sqlalchemy import select

from app.core.db import async_session
from app.models.monitor import Monitor
from app.models.result import CheckResult
from app.core.metrics import (
    updog_checks_total,
    updog_check_duration_seconds,
    updog_check_errors_total,
    updog_last_check_up,
    updog_monitors_total,
)


async def check_url(monitor: Monitor) -> CheckResult:
    """Check a single URL and return the result."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            start = datetime.utcnow()
            response = await client.get(str(monitor.url))
            elapsed_ms = int((datetime.utcnow() - start).total_seconds() * 1000)

            result = CheckResult(
                monitor_id=monitor.id,
                status_code=response.status_code,
                response_time_ms=elapsed_ms,
                is_up=response.status_code < 400,
                checked_at=datetime.utcnow(),
            )

            # Record metrics
            status = "up" if result.is_up else "down"
            updog_checks_total.labels(monitor_id=str(monitor.id), status=status).inc()
            updog_check_duration_seconds.labels(monitor_id=str(monitor.id)).observe(
                elapsed_ms / 1000
            )
            updog_last_check_up.labels(
                monitor_id=str(monitor.id), monitor_name=monitor.name
            ).set(1 if result.is_up else 0)

            return result
        except Exception as e:
            result = CheckResult(
                monitor_id=monitor.id,
                status_code=None,
                response_time_ms=None,
                is_up=False,
                checked_at=datetime.utcnow(),
                error_message=str(e),
            )

            # Record error metrics
            error_type = type(e).__name__
            updog_checks_total.labels(monitor_id=str(monitor.id), status="down").inc()
            updog_check_errors_total.labels(error_type=error_type).inc()
            updog_last_check_up.labels(
                monitor_id=str(monitor.id), monitor_name=monitor.name
            ).set(0)

            return result


async def run_checks():
    """Load all active monitors and check them."""
    async with async_session() as db:
        # Get all active monitors
        result = await db.execute(select(Monitor).where(Monitor.is_active == True))
        monitors = result.scalars().all()

        # Update monitor count gauge
        updog_monitors_total.labels(state="active").set(len(monitors))

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
