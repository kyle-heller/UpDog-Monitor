import os

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


# Skip DB-dependent tests in CI (no database available)
def pytest_configure(config):
    config.addinivalue_line("markers", "db_required: mark test as requiring database")


def pytest_collection_modifyitems(config, items):
    if os.environ.get("CI"):
        skip_db = pytest.mark.skip(reason="Database not available in CI")
        for item in items:
            if "db_required" in item.keywords:
                item.add_marker(skip_db)


@pytest.fixture
async def client():
    """Async test client for FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
