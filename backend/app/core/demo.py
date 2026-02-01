import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, delete

from app.core.config import settings
from app.core.db import async_session
from app.models.monitor import Monitor
from app.models.result import CheckResult


# Demo monitors with real, checkable URLs
DEMO_MONITORS = [
    {
        "name": "Google",
        "url": "https://google.com",
    },
    {
        "name": "GitHub",
        "url": "https://github.com",
    },
    {
        "name": "HTTPStat 200",
        "url": "https://httpstat.us/200",
    },
    {
        "name": "HTTPStat 500",
        "url": "https://httpstat.us/500",
    },
    {
        "name": "HTTPStat Random",
        "url": "https://httpstat.us/random/200,500",
    },
]

DAYS_OF_HISTORY = 7
CHECKS_PER_DAY = 96  # Every 15 minutes = 96 checks/day


def generate_check_result(
    monitor_id: int,
    monitor_name: str,
    checked_at: datetime,
) -> CheckResult:

    # HTTPStat 500 - always down
    if "500" in monitor_name and "Random" not in monitor_name:
        return CheckResult(
            monitor_id=monitor_id,
            status_code=500,
            response_time_ms=random.randint(100, 300),
            is_up=False,
            checked_at=checked_at,
            error_message="Internal Server Error",
        )

    # HTTPStat Random - 50% chance of failure
    if "Random" in monitor_name:
        is_up = random.random() > 0.5
        if is_up:
            return CheckResult(
                monitor_id=monitor_id,
                status_code=200,
                response_time_ms=random.randint(150, 400),
                is_up=True,
                checked_at=checked_at,
            )
        else:
            return CheckResult(
                monitor_id=monitor_id,
                status_code=500,
                response_time_ms=random.randint(150, 400),
                is_up=False,
                checked_at=checked_at,
                error_message="Internal Server Error",
            )

    # Google/GitHub/HTTPStat 200 - always up with occasional latency spikes
    base_latency = random.randint(30, 120)

    # 10% chance of latency spike
    if random.random() < 0.1:
        base_latency += random.randint(200, 500)

    return CheckResult(
        monitor_id=monitor_id,
        status_code=200,
        response_time_ms=base_latency,
        is_up=True,
        checked_at=checked_at,
    )


async def seed_demo_data() -> bool:
    """No-op if monitors already exist."""
    async with async_session() as db:
        existing = await db.execute(select(Monitor).limit(1))
        if existing.scalars().first():
            return False  # Already have data

        print("Demo mode: Seeding database with demo monitors...")

        monitors = []
        for data in DEMO_MONITORS:
            monitor = Monitor(
                name=data["name"],
                url=data["url"],
                interval_seconds=60,
                is_active=True,
            )
            db.add(monitor)
            monitors.append(monitor)

        await db.commit()

        for m in monitors:
            await db.refresh(m)

        print(f"Demo mode: Generating {DAYS_OF_HISTORY} days of historical data...")
        now = datetime.now(timezone.utc)

        for monitor in monitors:
            results = []
            for day in range(DAYS_OF_HISTORY):
                day_start = now - timedelta(days=day)

                for check_num in range(CHECKS_PER_DAY):
                    minutes_offset = 15 * check_num
                    checked_at = day_start.replace(
                        hour=0, minute=0, second=0, microsecond=0
                    ) + timedelta(minutes=minutes_offset)

                    if checked_at > now:
                        continue

                    result = generate_check_result(
                        monitor.id, monitor.name, checked_at
                    )
                    results.append(result)

            db.add_all(results)
            await db.commit()
            print(f"  ✓ {monitor.name}: {len(results)} historical checks")

        print("Demo mode: Seeding complete!")
        return True


async def cleanup_old_data() -> int:
    if not settings.demo_mode:
        return 0

    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.demo_retention_days)

    async with async_session() as db:
        result = await db.execute(
            delete(CheckResult).where(CheckResult.checked_at < cutoff)
        )
        await db.commit()

        deleted = result.rowcount
        if deleted > 0:
            print(f"Demo mode: Cleaned up {deleted} old check results")

        return deleted
