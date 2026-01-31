# Architecture Overview

## System Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           UpDog Monitor (Production)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────┐         ┌─────────────┐         ┌─────────────┐          │
│   │   React     │  HTTPS  │   FastAPI   │  SQL    │  PostgreSQL │          │
│   │  Frontend   │ ──────> │   Backend   │ ──────> │   Database  │          │
│   │  (Railway)  │  JSON   │  (Railway)  │         │  (Railway)  │          │
│   └─────────────┘         └──────┬──────┘         └─────────────┘          │
│                                  │                                          │
│                    ┌─────────────┼─────────────┐                           │
│                    │             │             │                            │
│                    ▼             ▼             ▼                            │
│             ┌──────────┐  ┌──────────┐  ┌──────────┐                       │
│             │ /metrics │  │  Worker  │  │ Discord  │                       │
│             │ endpoint │  │ (checks) │  │ Webhook  │                       │
│             └────┬─────┘  └────┬─────┘  └──────────┘                       │
│                  │             │                                            │
│                  ▼             ▼                                            │
│          ┌────────────┐  ┌──────────┐                                      │
│          │  Grafana   │  │ Target   │                                      │
│          │   Cloud    │  │  URLs    │                                      │
│          └────────────┘  └──────────┘                                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Production URLs

| Service | URL |
|---------|-----|
| Frontend | https://valiant-amazement-production-5a84.up.railway.app |
| Backend API | https://updog-monitor-production.up.railway.app |
| API Docs | https://updog-monitor-production.up.railway.app/docs |
| Metrics | https://updog-monitor-production.up.railway.app/metrics (auth required) |
| Grafana | Grafana Cloud (kylehellerdev stack) |

## Components

### Backend (FastAPI)

**Purpose:** REST API for managing monitors and retrieving results.

**Responsibilities:**
- CRUD operations for monitors
- Query check results and statistics
- Expose Prometheus metrics (with basic auth)
- Health check endpoint
- SLO calculations and error budgets

**Key Files:**
```
backend/app/
├── main.py              # FastAPI app, lifespan, middleware, metrics auth
├── api/
│   ├── monitors.py      # Monitor CRUD endpoints
│   ├── health.py        # Health check endpoint
│   └── slo.py           # SLO report endpoints
├── models/
│   ├── monitor.py       # Monitor SQLAlchemy model
│   └── result.py        # CheckResult SQLAlchemy model
├── core/
│   ├── config.py        # Pydantic Settings (DB, Discord, metrics auth)
│   ├── db.py            # Database engine, session
│   ├── metrics.py       # Prometheus metric definitions
│   ├── notifications.py # Discord webhook alerts
│   └── slo.py           # SLO calculation logic
└── worker/
    └── checker.py       # Background URL checker
```

### Worker (Background Process)

**Purpose:** Periodically ping monitored URLs and store results.

**Responsibilities:**
- Run on a schedule (default: every 60 seconds)
- HTTP GET each active monitor's URL
- Record status code, response time, success/failure
- Trigger Discord alerts on status change
- Update Prometheus metrics

**Design Decision:** Using APScheduler for simplicity. Could migrate to Celery if needed for scale.

### Database (PostgreSQL)

**Purpose:** Persistent storage for monitors and check results.

**Tables:**
- `monitors` — URLs to monitor
- `check_results` — Historical check data

See [Data Model](./data-model.md) for full schema.

### Frontend (React + TypeScript)

**Purpose:** Web UI for viewing monitors and status.

**Pages:**
- Dashboard — Overview of all monitors with status cards
- Monitor Detail — Check history, response time charts, SLO status
- Add/Edit Monitor — Form to manage monitors

**Key Files:**
```
frontend/src/
├── pages/
│   ├── Dashboard.tsx    # Monitor list with status
│   └── MonitorDetail.tsx # History, charts, SLOs
├── components/
│   ├── MonitorCard.tsx  # Status card component
│   ├── MonitorForm.tsx  # Add/edit form
│   └── ResponseTimeChart.tsx # Recharts visualization
└── api/
    └── monitors.ts      # API client functions
```

### Monitoring (Grafana Cloud)

**Purpose:** Visualize metrics and set up alerting.

**Setup:**
- Grafana Cloud free tier (kylehellerdev stack)
- Hosted Collector scrapes `/metrics` endpoint every minute
- Basic auth protects metrics endpoint

**Dashboard Panels:**
- Active monitors count
- Monitor up/down status
- Availability percentage
- Response time (p50, p95)
- Error rate by type
- API request rate and latency

**File:** `grafana-dashboard.json` (importable)

### CI/CD (GitHub Actions)

**Purpose:** Automated testing and linting on every push.

**Workflow:** `.github/workflows/ci.yml`
- Runs on push to main and PRs
- Lints with Ruff
- Runs pytest test suite
- DB-dependent tests skipped in CI (no database available)

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
    For each monitor (concurrent):
         │
         ├──> HTTP GET to URL
         │
         ├──> Record: status_code, response_time, is_up
         │
         ├──> Update Prometheus metrics
         │
         ├──> If state changed: send Discord alert
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

### Metrics Flow

```
Grafana Cloud Hosted Collector
         │
         │ (every 60s, with basic auth)
         ▼
    GET /metrics → FastAPI → prometheus_client
         │
         ▼
    Grafana Cloud Prometheus storage
         │
         ▼
    Grafana Dashboards
```

## Technology Choices

| Choice | Alternatives Considered | Why This One |
|--------|------------------------|--------------|
| FastAPI | Flask, Django | Async, modern, great docs, matches learning goals |
| PostgreSQL | SQLite, MySQL | Industry standard, matches production patterns |
| SQLAlchemy | Raw SQL, Tortoise | Most common Python ORM, good to know |
| APScheduler | Celery, cron | Simple, in-process, good enough for this scale |
| React | Vue, Svelte | Most jobs require it, largest ecosystem |
| Railway | Render, Fly.io | Simple deployment, good free tier, PostgreSQL included |
| Grafana Cloud | Self-hosted Grafana | Managed service, free tier, no infrastructure to maintain |
| Docker Compose | Local installs | Reproducible, easy database setup |

## Environment Variables

### Backend (Railway)

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string (auto-set by Railway) |
| `DISCORD_WEBHOOK_URL` | Discord alerts (optional) |
| `METRICS_USERNAME` | Basic auth for /metrics |
| `METRICS_PASSWORD` | Basic auth for /metrics |
| `PORT` | Server port (auto-set by Railway) |

### Frontend (Build-time)

| Variable | Purpose |
|----------|---------|
| `VITE_API_URL` | Backend API URL (in `.env.production`) |
