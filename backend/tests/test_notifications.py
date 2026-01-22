"""Tests for notification service."""

import pytest
from unittest.mock import patch, AsyncMock

from app.core.notifications import send_discord_alert


@pytest.mark.asyncio
async def test_send_discord_alert_skips_when_no_webhook():
    """Alert should return False when webhook URL not configured."""
    with patch("app.core.notifications.settings") as mock_settings:
        mock_settings.discord_webhook_url = None

        result = await send_discord_alert(
            monitor_name="Test",
            url="https://example.com",
            is_up=False,
        )

        assert result is False


@pytest.mark.asyncio
async def test_send_discord_alert_formats_down_alert():
    """DOWN alert should have red color and appropriate message."""
    with patch("app.core.notifications.settings") as mock_settings, \
         patch("app.core.notifications.httpx.AsyncClient") as mock_client:

        mock_settings.discord_webhook_url = "https://discord.com/api/webhooks/test"

        mock_response = AsyncMock()
        mock_response.status_code = 204
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )

        result = await send_discord_alert(
            monitor_name="Test Monitor",
            url="https://example.com",
            is_up=False,
            error_message="Connection refused",
        )

        assert result is True

        # Verify the call was made
        call_args = mock_client.return_value.__aenter__.return_value.post.call_args
        payload = call_args.kwargs["json"]

        assert payload["username"] == "UpDog Monitor"
        assert "DOWN" in payload["embeds"][0]["title"]
        assert payload["embeds"][0]["color"] == 15158332  # Red


@pytest.mark.asyncio
async def test_send_discord_alert_formats_recovery_alert():
    """RECOVERED alert should have green color."""
    with patch("app.core.notifications.settings") as mock_settings, \
         patch("app.core.notifications.httpx.AsyncClient") as mock_client:

        mock_settings.discord_webhook_url = "https://discord.com/api/webhooks/test"

        mock_response = AsyncMock()
        mock_response.status_code = 204
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )

        result = await send_discord_alert(
            monitor_name="Test Monitor",
            url="https://example.com",
            is_up=True,
            response_time_ms=150,
        )

        assert result is True

        call_args = mock_client.return_value.__aenter__.return_value.post.call_args
        payload = call_args.kwargs["json"]

        assert "RECOVERED" in payload["embeds"][0]["title"]
        assert payload["embeds"][0]["color"] == 3066993  # Green
