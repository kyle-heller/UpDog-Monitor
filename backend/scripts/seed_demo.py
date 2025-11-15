"""
Seed script to populate the database with demo data.
Creates monitors and generates realistic check history.

Run from backend directory:
    python scripts/seed_demo.py
"""

import asyncio
import random
from datetime import datetime, timedelta

from sqlalchemy import select

from app.core.db import async_session
from app.models.monitor import Monitor
from app.models.result import CheckResult


# Demo monitors to create
DEMO_MONITORS = [
    {"name": "Google", "url": "https://google.com"},
    {"name": "GitHub", "url": "https://github.com"},
    {"name": "Example API", "url": "https://api.example.com"},
    {"name": "Internal Service", "url": "https://internal.example.com"},
]

# How much history to generate
DAYS_OF_HISTORY = 14
CHECKS_PER_DAY = 60  # One per minute = 1440, but we'll sample


def generate_check_result(
    monitor_id: int, checked_at: datetime, is_flaky: bool = False
) -> CheckResult:
    """Generate a realistic check result."""

    # Simulate occasional outages
    if is_flaky and random.random() < 0.05:  # 5% failure rate for flaky services
        return CheckResult(
            monitor_id=monitor_id,
            status_code=None,
            response_time_ms=None,
            is_up=False,
            checked_at=checked_at,
            error_message=random.choice(
                [
                    "Connection timeout",
                    "Connection refused",
                    "DNS resolution failed",
                ]
            ),
        )

    # Simulate normal responses with varying latency
    base_latency = random.randint(50, 150)

    # Add occasional latency spikes
    if random.random() < 0.1:  # 10% chance of slow response
        base_latency += random.randint(200, 500)

    return CheckResult(
        monitor_id=monitor_id,
        status_code=200,
        response_time_ms=base_latency,
        is_up=True,
        checked_at=checked_at,
    )


async def seed_database():
    """Main seeding function."""
    async with async_session() as db:
        # Check if we already have monitors
        existing = await db.execute(select(Monitor))
        if existing.scalars().first():
            print("Database already has data. Clear it first if you want to reseed.")
            print("Run: DELETE FROM check_results; DELETE FROM monitors;")
            return

        print(f"Creating {len(DEMO_MONITORS)} monitors...")

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

        # Refresh to get IDs
        for m in monitors:
            await db.refresh(m)

        print(f"Generating {DAYS_OF_HISTORY} days of check history...")

        now = datetime.utcnow()
        total_results = 0

        for monitor in monitors:
            # Make some monitors "flaky" for interesting data
            is_flaky = monitor.name in ["Example API", "Internal Service"]

            for day in range(DAYS_OF_HISTORY):
                day_start = now - timedelta(days=day)

                for check_num in range(CHECKS_PER_DAY):
                    # Spread checks throughout the day
                    minutes_offset = (24 * 60 // CHECKS_PER_DAY) * check_num
                    checked_at = day_start.replace(
                        hour=0, minute=0, second=0
                    ) + timedelta(minutes=minutes_offset)

                    result = generate_check_result(monitor.id, checked_at, is_flaky)
                    db.add(result)
                    total_results += 1

            await db.commit()
            print(f"  ✓ {monitor.name}: {DAYS_OF_HISTORY * CHECKS_PER_DAY} results")

        print(f"\nDone! Created {total_results} check results.")


if __name__ == "__main__":
    asyncio.run(seed_database())
