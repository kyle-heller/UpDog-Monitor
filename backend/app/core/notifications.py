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

    if not settings.discord_webhook_url:
        return False

    if is_up:
        color = 3066993  # Green
        status = "✅ RECOVERED"
        description = f"**{monitor_name}** is back online!"
    else:
        color = 15158332  # Red
        status = "🔴 DOWN"
        description = f"**{monitor_name}** is not responding!"

    embed = {
        "title": status,
        "description": description,
        "color": color,
        "fields": [
            {"name": "URL", "value": url, "inline": True},
        ],
    }

    if error_message:
        embed["fields"].append({
            "name": "Error",
            "value": f"```{error_message[:200]}```",  # Truncate long errors
            "inline": False,
        })

    if response_time_ms is not None:
        embed["fields"].append({
            "name": "Response Time",
            "value": f"{response_time_ms}ms",
            "inline": True,
        })

    payload = {
        "username": "UpDog Monitor",
        "embeds": [embed],
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                settings.discord_webhook_url,
                json=payload,
            )
            if response.status_code == 204:
                alert_type = "recovered" if is_up else "down"
                updog_alerts_total.labels(alert_type=alert_type).inc()
                return True
            return False
    except Exception as e:
        print(f"Failed to send Discord alert: {e}")
        return False
