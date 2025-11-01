# Architecture Overview

## System Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           UpDog Monitor                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────┐         ┌─────────────┐         ┌─────────────┐       │
│   │   React     │  HTTP   │   FastAPI   │  SQL    │  PostgreSQL │       │
│   │  Frontend   │ ──────> │   Backend   │ ──────> │   Database  │       │
│   │  (v0.2+)    │  JSON   │             │         │             │       │
│   └─────────────┘         └──────┬──────┘         └─────────────┘       │
│                                  │                                       │
│                                  │                                       │
│                           ┌──────┴──────┐                               │
│                           │   Worker    │                               │
│                           │  (Background)│                               │
│                           └──────┬──────┘                               │
│                                  │                                       │
│                    ┌─────────────┼─────────────┐                        │
│                    │             │             │                         │
│                    ▼             ▼             ▼                         │
│              ┌──────────┐ ┌──────────┐ ┌──────────┐                     │
│              │ Target 1 │ │ Target 2 │ │ Target N │                     │
│              │  (URL)   │ │  (URL)   │ │  (URL)   │                     │
│              └──────────┘ └──────────┘ └──────────┘                     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Components

### Backend (FastAPI)

**Purpose:** REST API for managing monitors and retrieving results.

**Responsibilities:**
- CRUD operations for monitors
- Query check results and statistics
- Expose Prometheus metrics (v0.4+)
- Health check endpoint

**Key Files:**
```
backend/app/
├── main.py          # FastAPI app, lifespan, middleware
├── api/
│   ├── routes.py    # Main router
│   ├── monitors.py  # Monitor CRUD endpoints
│   └── health.py    # Health check endpoint
├── models/
│   ├── monitor.py   # Monitor SQLAlchemy model
│   └── result.py    # CheckResult SQLAlchemy model
├── core/
│   ├── config.py    # Pydantic Settings
│   └── db.py        # Database engine, session
└── worker/
    └── checker.py   # Background URL checker
```

### Worker (Background Process)

**Purpose:** Periodically ping monitored URLs and store results.

**Responsibilities:**
- Run on a schedule (default: every 60 seconds)
- HTTP GET each active monitor's URL
- Record status code, response time, success/failure
- Trigger Discord alerts on status change (v0.6+)

**Design Decision:** Using APScheduler for simplicity. Could migrate to Celery if needed for scale.

### Database (PostgreSQL)

**Purpose:** Persistent storage for monitors and check results.

**Tables:**
- `monitors` — URLs to monitor
- `check_results` — Historical check data

See [Data Model](./data-model.md) for full schema.

### Frontend (React) — v0.2+

**Purpose:** Web UI for viewing monitors and status.

**Pages:**
- Dashboard — Overview of all monitors
- Monitor Detail — Check history and stats
- Add/Edit Monitor — Form to manage monitors

## Data Flow

### Adding a Monitor

```
User → React UI → POST /api/monitors → FastAPI → PostgreSQL
                                                      │
                                                      ▼
                                              monitors table
```

### Checking URLs (Background)

```
Scheduler triggers every 60s
         │
         ▼
    Worker loads active monitors from DB
         │
         ▼
    For each monitor:
         │
         ├──> HTTP GET to URL
         │
         ├──> Record: status_code, response_time, is_up
         │
         └──> INSERT into check_results
```

### Viewing Status

```
User → React UI → GET /api/monitors/{id}/results → FastAPI → PostgreSQL
                                                                  │
                                                                  ▼
                         React renders ← JSON response ← check_results
```

## Technology Choices

| Choice | Alternatives Considered | Why This One |
|--------|------------------------|--------------|
| FastAPI | Flask, Django | Async, modern, great docs, matches learning goals |
| PostgreSQL | SQLite, MySQL | Industry standard, matches production patterns |
| SQLAlchemy | Raw SQL, Tortoise | Most common Python ORM, good to know |
| APScheduler | Celery, cron | Simple, in-process, good enough for this scale |
| React | Vue, Svelte | Most jobs require it, largest ecosystem |
| Docker Compose | Local installs | Reproducible, easy database setup |

## Future Additions

| Version | Addition |
|---------|----------|
| 0.4 | Prometheus `/metrics` endpoint |
| 0.6 | Discord webhook notifications |
| 0.7 | User authentication |
| 0.8 | Kubernetes deployment |
| 1.0 | Azure AKS with live demo |
