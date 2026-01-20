
import pytest


@pytest.mark.asyncio
async def test_root_endpoint(client):
    response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "What's updog?"}


@pytest.mark.asyncio
@pytest.mark.db_required
async def test_health_endpoint(client):
    response = await client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
@pytest.mark.db_required
async def test_list_monitors_endpoint(client):
    response = await client.get("/api/monitors")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
@pytest.mark.db_required
async def test_get_nonexistent_monitor_returns_404(client):
    response = await client.get("/api/monitors/99999")

    assert response.status_code == 404
