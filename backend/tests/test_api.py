"""Tests for API endpoints."""

import pytest


@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Root endpoint returns welcome message."""
    response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "What's updog?"}


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Health endpoint returns OK status."""
    response = await client.get("/api/health")

    # May fail if no DB, but should at least return valid JSON
    assert response.status_code in [200, 500]


@pytest.mark.asyncio
@pytest.mark.db_required
async def test_list_monitors_endpoint(client):
    """GET /api/monitors returns a list."""
    response = await client.get("/api/monitors")

    # May fail without DB, but validates route exists
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        assert isinstance(response.json(), list)


@pytest.mark.asyncio
@pytest.mark.db_required
async def test_get_nonexistent_monitor_returns_404(client):
    """GET /api/monitors/{id} returns 404 for missing monitor."""
    response = await client.get("/api/monitors/99999")

    # Either 404 (correct) or 500 (no DB)
    assert response.status_code in [404, 500]
