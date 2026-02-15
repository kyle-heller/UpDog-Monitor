from prometheus_client import Counter, Gauge, Histogram

updog_checks_total = Counter(
    "updog_checks_total",
    "Total URL checks performed",
    ["monitor_id", "status", "status_code"],
)

updog_check_duration_seconds = Histogram(
    "updog_check_duration_seconds",
    "Response time of monitored URLs in seconds",
    ["monitor_id"],
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

updog_monitors_total = Gauge(
    "updog_monitors_total",
    "Number of configured monitors",
    ["state"],
)

updog_check_errors_total = Counter(
    "updog_check_errors_total",
    "Total check failures by error type",
    ["error_type"],
)

updog_last_check_up = Gauge(
    "updog_last_check_up",
    "Current status of monitor (1=up, 0=down)",
    ["monitor_id", "monitor_name"],
)

updog_alerts_total = Counter(
    "updog_alerts_total",
    "Total alerts sent",
    ["alert_type"],  # "down" or "recovered"
)
