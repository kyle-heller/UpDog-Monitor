# Usage: DATABASE_URL="..." PYTHONPATH=. python scripts/reset_demo.py

import asyncio
import os
from sqlalchemy import text

if os.environ.get("DATABASE_URL"):
    os.environ["DATABASE_URL"] = os.environ["DATABASE_URL"].replace(
        "postgresql://", "postgresql+asyncpg://"
    )

from app.core.db import async_session
from app.core.demo import seed_demo_data


async def reset_database():
    print("Clearing database...")
    async with async_session() as db:
        await db.execute(text("DELETE FROM check_results"))
        await db.execute(text("DELETE FROM monitors"))
        await db.commit()
    print("Database cleared!")

    print("Seeding demo data...")
    await seed_demo_data()
    print("Done!")


if __name__ == "__main__":
    asyncio.run(reset_database())
