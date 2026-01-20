"""Tests for Prometheus metrics endpoint."""

import pytest


@pytest.mark.asyncio
async def test_metrics_endpoint_returns_prometheus_format(client):
    """The /metrics endpoint should return Prometheus text format."""
    response = await client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]

    # Should contain standard Prometheus metrics
    content = response.text
    assert "# HELP" in content
    assert "# TYPE" in content


@pytest.mark.asyncio
async def test_metrics_contains_custom_updog_metrics(client):
    """Custom UpDog metrics should be registered."""
    response = await client.get("/metrics")
    content = response.text

    # Our custom metrics should be present
    assert "updog_checks_total" in content
    assert "updog_monitors_total" in content
    assert "updog_check_duration_seconds" in content
