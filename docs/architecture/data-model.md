# Data Model

## Overview

UpDog Monitor uses two main tables:

1. **monitors** — URLs to monitor
2. **check_results** — Historical check data

## Entity Relationship Diagram

```
┌─────────────────────────────┐
│          monitors           │
├─────────────────────────────┤
│ id (UUID, PK)               │
│ url (VARCHAR)               │
│ name (VARCHAR)              │
│ interval_seconds (INT)      │
│ is_active (BOOLEAN)         │
│ created_at (TIMESTAMP)      │
│ updated_at (TIMESTAMP)      │
└──────────────┬──────────────┘
               │
               │ 1:N
               │
               ▼
┌─────────────────────────────┐
│       check_results         │
├─────────────────────────────┤
│ id (UUID, PK)               │
│ monitor_id (UUID, FK)       │
│ status_code (INT)           │
│ response_time_ms (INT)      │
│ is_up (BOOLEAN)             │
│ error_message (TEXT)        │
│ checked_at (TIMESTAMP)      │
└─────────────────────────────┘
```

## Table Definitions

### monitors

Stores the URLs to be monitored.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| url | VARCHAR(2048) | NOT NULL | Full URL to monitor (e.g., `https://example.com/health`) |
| name | VARCHAR(255) | NOT NULL | Friendly name for display |
| interval_seconds | INTEGER | NOT NULL, DEFAULT 60 | How often to check (in seconds) |
| is_active | BOOLEAN | NOT NULL, DEFAULT true | Whether monitoring is enabled |
| created_at | TIMESTAMP | NOT NULL, DEFAULT now() | When the monitor was created |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT now() | When the monitor was last updated |

**Indexes:**
- `idx_monitors_is_active` on `is_active` — Fast lookup of active monitors

### check_results

Stores the results of each URL check.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| monitor_id | UUID | NOT NULL, FOREIGN KEY | Reference to monitors table |
| status_code | INTEGER | NULL | HTTP status code (null if request failed) |
| response_time_ms | INTEGER | NULL | Response time in milliseconds |
| is_up | BOOLEAN | NOT NULL | Whether the check succeeded |
| error_message | TEXT | NULL | Error details if check failed |
| checked_at | TIMESTAMP | NOT NULL, DEFAULT now() | When the check was performed |

**Indexes:**
- `idx_check_results_monitor_id` on `monitor_id` — Fast lookup by monitor
- `idx_check_results_checked_at` on `checked_at` — Fast time-range queries
- `idx_check_results_monitor_checked` on `(monitor_id, checked_at DESC)` — Fast latest results per monitor

## SQLAlchemy Models

### Monitor

```python
class Monitor(Base):
    __tablename__ = "monitors"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    interval_seconds: Mapped[int] = mapped_column(Integer, default=60)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    results: Mapped[list["CheckResult"]] = relationship(back_populates="monitor")
```

### CheckResult

```python
class CheckResult(Base):
    __tablename__ = "check_results"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    monitor_id: Mapped[UUID] = mapped_column(ForeignKey("monitors.id"), nullable=False)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_up: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    checked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationship
    monitor: Mapped["Monitor"] = relationship(back_populates="results")
```

## Sample Data

### monitors

| id | url | name | interval_seconds | is_active |
|----|-----|------|------------------|-----------|
| abc-123 | https://api.example.com/health | Example API | 60 | true |
| def-456 | https://google.com | Google | 300 | true |
| ghi-789 | https://old-service.internal | Legacy Service | 60 | false |

### check_results

| id | monitor_id | status_code | response_time_ms | is_up | error_message | checked_at |
|----|------------|-------------|------------------|-------|---------------|------------|
| r-001 | abc-123 | 200 | 45 | true | null | 2025-01-28 10:00:00 |
| r-002 | abc-123 | 200 | 52 | true | null | 2025-01-28 10:01:00 |
| r-003 | abc-123 | 500 | 1203 | false | "Internal Server Error" | 2025-01-28 10:02:00 |
| r-004 | def-456 | 200 | 89 | true | null | 2025-01-28 10:00:00 |

## Queries

### Get all active monitors

```sql
SELECT * FROM monitors WHERE is_active = true;
```

### Get latest result for each monitor

```sql
SELECT DISTINCT ON (monitor_id) *
FROM check_results
ORDER BY monitor_id, checked_at DESC;
```

### Get uptime percentage (last 24 hours)

```sql
SELECT 
    monitor_id,
    COUNT(*) as total_checks,
    SUM(CASE WHEN is_up THEN 1 ELSE 0 END) as successful_checks,
    ROUND(100.0 * SUM(CASE WHEN is_up THEN 1 ELSE 0 END) / COUNT(*), 2) as uptime_pct
FROM check_results
WHERE checked_at > NOW() - INTERVAL '24 hours'
GROUP BY monitor_id;
```

### Get average response time (last hour)

```sql
SELECT 
    monitor_id,
    AVG(response_time_ms) as avg_response_ms
FROM check_results
WHERE checked_at > NOW() - INTERVAL '1 hour'
  AND is_up = true
GROUP BY monitor_id;
```
