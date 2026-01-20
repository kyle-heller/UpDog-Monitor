import asyncio
import time
from datetime import datetime, timezone

import httpx
from sqlalchemy import select, desc

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
from app.core.notifications import send_discord_alert


async def get_previous_state(db, monitor_id: int) -> bool | None:
    result = await db.execute(
        select(CheckResult)
        .where(CheckResult.monitor_id == monitor_id)
        .order_by(desc(CheckResult.checked_at))
        .limit(1)
    )
    last_check = result.scalar_one_or_none()
    return last_check.is_up if last_check else None


async def _do_check(monitor: Monitor, client: httpx.AsyncClient) -> CheckResult:
    try:
        start = time.monotonic()
        response = await client.get(str(monitor.url))
        elapsed_ms = int((time.monotonic() - start) * 1000)

        result = CheckResult(
            monitor_id=monitor.id,
            status_code=response.status_code,
            response_time_ms=elapsed_ms,
            is_up=response.status_code < 400,
            checked_at=datetime.now(timezone.utc),
        )

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
            checked_at=datetime.now(timezone.utc),
            error_message=str(e),
        )

        error_type = type(e).__name__
        updog_checks_total.labels(monitor_id=str(monitor.id), status="down").inc()
        updog_check_errors_total.labels(error_type=error_type).inc()
        updog_last_check_up.labels(
            monitor_id=str(monitor.id), monitor_name=monitor.name
        ).set(0)

        return result


async def check_url(monitor: Monitor, client: httpx.AsyncClient | None = None) -> CheckResult:
    if client is not None:
        return await _do_check(monitor, client)
    async with httpx.AsyncClient(timeout=30.0) as c:  # TODO: configurable timeout per monitor
        return await _do_check(monitor, c)


async def run_checks():
    async with async_session() as db:
        # Get all active monitors
        result = await db.execute(select(Monitor).where(Monitor.is_active.is_(True)))
        monitors = result.scalars().all()

        updog_monitors_total.labels(state="active").set(len(monitors))

        if not monitors:
            print("No active monitors to check")
            return

        print(f"Checking {len(monitors)} monitors...")

        # Get previous states before running checks
        previous_states = {}
        for monitor in monitors:
            previous_states[monitor.id] = await get_previous_state(db, monitor.id)

        async with httpx.AsyncClient(timeout=30.0) as client:
            tasks = [check_url(monitor, client) for monitor in monitors]
            results = await asyncio.gather(*tasks)

        alert_tasks = []
        for monitor, check_result in zip(monitors, results):
            db.add(check_result)

            previous_up = previous_states.get(monitor.id)

            if previous_up is not None and previous_up != check_result.is_up:
                print(
                    f"State change for {monitor.name}: "
                    f"{'UP' if previous_up else 'DOWN'} → "
                    f"{'UP' if check_result.is_up else 'DOWN'}"
                )
                alert_tasks.append(
                    send_discord_alert(
                        monitor_name=monitor.name,
                        url=str(monitor.url),
                        is_up=check_result.is_up,
                        error_message=check_result.error_message,
                        response_time_ms=check_result.response_time_ms,
                    )
                )

        await db.commit()
        print(f"Saved {len(results)} check results")

        if alert_tasks:
            await asyncio.gather(*alert_tasks)
            print(f"Sent {len(alert_tasks)} alerts")
