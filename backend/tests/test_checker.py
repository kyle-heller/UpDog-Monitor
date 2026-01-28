"""Tests for URL checker logic."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.worker.checker import check_url


class MockMonitor:
    """Mock monitor for testing."""
    def __init__(self, id=1, name="Test", url="https://example.com"):
        self.id = id
        self.name = name
        self.url = url


@pytest.mark.asyncio
async def test_check_url_success():
    """Successful URL check returns is_up=True with status code."""
    monitor = MockMonitor()

    with patch("app.worker.checker.httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        result = await check_url(monitor)

        assert result.is_up is True
        assert result.status_code == 200
        assert result.monitor_id == 1
        assert result.response_time_ms is not None
        assert result.error_message is None


@pytest.mark.asyncio
async def test_check_url_failure_status_code():
    """URL returning 500 should be marked as down."""
    monitor = MockMonitor()

    with patch("app.worker.checker.httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        result = await check_url(monitor)

        assert result.is_up is False
        assert result.status_code == 500


@pytest.mark.asyncio
async def test_check_url_connection_error():
    """Connection error should be marked as down with error message."""
    monitor = MockMonitor()

    with patch("app.worker.checker.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=Exception("Connection refused")
        )

        result = await check_url(monitor)

        assert result.is_up is False
        assert result.status_code is None
        assert result.response_time_ms is None
        assert "Connection refused" in result.error_message


@pytest.mark.asyncio
async def test_check_url_404_is_down():
    """404 response should be marked as down."""
    monitor = MockMonitor()

    with patch("app.worker.checker.httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        result = await check_url(monitor)

        assert result.is_up is False
        assert result.status_code == 404


@pytest.mark.asyncio
async def test_check_url_redirect_is_up():
    """3xx redirects should still be considered up."""
    monitor = MockMonitor()

    with patch("app.worker.checker.httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 301

        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        result = await check_url(monitor)

        assert result.is_up is True
        assert result.status_code == 301
