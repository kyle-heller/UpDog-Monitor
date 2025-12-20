"""
Discord notification service for UpDog Monitor.

Discord webhooks accept POST requests with JSON body.
We use "embeds" for rich formatting (colored cards with fields).

Webhook URL format: https://discord.com/api/webhooks/{id}/{token}
"""

import httpx
from app.core.config import settings
from app.core.metrics import updog_alerts_total


async def send_discord_alert(
    monitor_name: str,
    url: str,
    is_up: bool,
    error_message: str | None = None,
    response_time_ms: int | None = None,
) -> bool:
    """
    Send an alert to Discord when monitor state changes.

    Returns True if sent successfully, False otherwise.
    Fails silently if webhook URL not configured (alerts disabled).
    """
    # If no webhook configured, skip silently
    if not settings.discord_webhook_url:
        return False

    # Choose color and status based on state
    # Discord uses decimal colors: green=3066993, red=15158332
    if is_up:
        color = 3066993  # Green
        status = "✅ RECOVERED"
        description = f"**{monitor_name}** is back online!"
    else:
        color = 15158332  # Red
        status = "🔴 DOWN"
        description = f"**{monitor_name}** is not responding!"

    # Build the embed (Discord's rich message format)
    embed = {
        "title": status,
        "description": description,
        "color": color,
        "fields": [
            {"name": "URL", "value": url, "inline": True},
        ],
    }

    # Add error message if present (for DOWN alerts)
    if error_message:
        embed["fields"].append({
            "name": "Error",
            "value": f"```{error_message[:200]}```",  # Truncate long errors
            "inline": False,
        })

    # Add response time if present (for RECOVERED alerts)
    if response_time_ms is not None:
        embed["fields"].append({
            "name": "Response Time",
            "value": f"{response_time_ms}ms",
            "inline": True,
        })

    # Discord webhook payload
    payload = {
        "username": "UpDog Monitor",
        "embeds": [embed],
    }

    # Send to Discord
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                settings.discord_webhook_url,
                json=payload,
            )
            # Discord returns 204 No Content on success
            if response.status_code == 204:
                # Record metric for successful alert
                alert_type = "recovered" if is_up else "down"
                updog_alerts_total.labels(alert_type=alert_type).inc()
                return True
            return False
    except Exception as e:
        # Log but don't crash - alerting shouldn't break monitoring
        print(f"Failed to send Discord alert: {e}")
        return False
