# Usage: PYTHONPATH=. python scripts/seed_demo.py

import asyncio
from app.core.demo import seed_demo_data


async def main():
    print("Manual demo data seeding...")
    result = await seed_demo_data()
    if not result:
        print("Database already has monitors. Clear them first to reseed:")
        print("  DELETE FROM check_results; DELETE FROM monitors;")


if __name__ == "__main__":
    asyncio.run(main())
