"""Clear all data from the database."""

import asyncio

from sqlalchemy import text

from app.core.db import async_session


async def clear():
    async with async_session() as db:
        await db.execute(text('DELETE FROM check_results'))
        await db.execute(text('DELETE FROM monitors'))
        await db.commit()
        print('Database cleared!')


if __name__ == "__main__":
    asyncio.run(clear())
