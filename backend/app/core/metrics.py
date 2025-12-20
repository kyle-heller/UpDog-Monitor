from prometheus_client import Counter, Gauge, Histogram

# Custom business metrics for URL monitoring

# Counts each URL check, labeled by monitor_id and status (up/down)
updog_checks_total = Counter(
    "updog_checks_total",
    "Total URL checks performed",
    ["monitor_id", "status"],
)

# Histogram of response times for monitored URLs
updog_check_duration_seconds = Histogram(
    "updog_check_duration_seconds",
    "Response time of monitored URLs in seconds",
    ["monitor_id"],
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# Gauge for total number of monitors by active/inactive state
updog_monitors_total = Gauge(
    "updog_monitors_total",
    "Number of configured monitors",
    ["state"],
)

# Counter for check errors by error type
updog_check_errors_total = Counter(
    "updog_check_errors_total",
    "Total check failures by error type",
    ["error_type"],
)

# Gauge showing current status per monitor (1=up, 0=down)
updog_last_check_up = Gauge(
    "updog_last_check_up",
    "Current status of monitor (1=up, 0=down)",
    ["monitor_id", "monitor_name"],
)

# Counter for alerts sent by type (down/recovered)
updog_alerts_total = Counter(
    "updog_alerts_total",
    "Total alerts sent",
    ["alert_type"],  # "down" or "recovered"
)
