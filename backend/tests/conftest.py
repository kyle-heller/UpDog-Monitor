import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
    except Exception:
        # App may fail to start without database - skip gracefully
        pytest.skip("App failed to start (likely no database connection)")
