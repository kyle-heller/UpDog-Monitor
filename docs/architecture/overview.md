# Architecture Overview

## System Diagram

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           UpDog Monitor (Production)                              │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│   ┌─────────────┐         ┌─────────────┐         ┌─────────────┐               │
│   │   React     │  HTTPS  │   FastAPI   │  SQL    │  PostgreSQL │               │
│   │  Frontend   │ ──────> │   Backend   │ ──────> │   Database  │               │
│   │  (Railway)  │  JSON   │  (Railway)  │         │  (Railway)  │               │
│   └─────────────┘         └──────┬──────┘         └─────────────┘               │
│                                  │                                                │
│                    ┌─────────────┼──────────────┬─────────────┐                  │
│                    │             │              │             │                   │
│                    ▼             ▼              ▼             ▼                   │
│             ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐           │
│             │ /metrics │  │  Worker  │  │ Discord  │  │   Azure     │           │
│             │ endpoint │  │ (checks) │  │ Webhook  │  │  Monitor    │           │
│             └────┬─────┘  └────┬─────┘  └─────▲────┘  │ (OTel SDK) │           │
│                  │             │               │       └──────┬──────┘           │
│                  ▼             ▼               │              ▼                   │
│          ┌────────────┐  ┌──────────┐  ┌──────┴─────┐  ┌────────────┐           │
│          │ Prometheus │  │ Target   │  │ Alert-     │  │    Log     │           │
│          │ + Grafana  │  │  URLs    │  │ manager    │  │ Analytics  │           │
│          └────────────┘  └──────────┘  └────────────┘  └────────────┘           │
│                                                                                   │
└──────────────────────────────────────────────────────────────────────────────────┘
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


### Database (PostgreSQL)

**Purpose:** Persistent storage for monitors and check results.

**Tables:**
- `monitors` - URLs to monitor
- `check_results` - Historical check data

See the model definitions in `backend/app/models/` for full schema.

### Frontend (React + TypeScript)

**Purpose:** Web UI for viewing monitors and status.

**Pages:**
- Dashboard - Overview of all monitors with status cards
- Monitor Detail - Check history, response time charts, SLO status
- Add/Edit Monitor - Form to manage monitors

**Key Files:**
```
frontend/src/
├── pages/
│   ├── Dashboard.tsx
│   ├── MonitorDetail.tsx
│   └── AddMonitor.tsx
└── api/
    └── monitors.ts
```

### Monitoring (Prometheus + Grafana)

**Purpose:** Visualize metrics, track SLOs, and alert on threshold breaches.

**Setup:**
- Prometheus scrapes `/metrics` endpoint every 15 seconds
- Alerting rules evaluate SLO thresholds (availability, latency, burn rate)
- Alertmanager routes firing alerts to Discord webhook
- Grafana Cloud free tier (kylehellerdev stack) for dashboards
- Basic auth protects metrics endpoint

**Dashboard Panels:**
- Active monitors count
- Monitor up/down status
- Availability percentage (SLO compliance)
- Response time (p50, p95, p99)
- Error budget remaining and burn rate
- Alert state table (firing/pending/OK)
- Error rate by type
- API request rate and latency

**Key Files:**
- `grafana-dashboard.json` - Importable dashboard
- `prometheus/alerts.yml` - SLO alerting rules
- `prometheus/alertmanager.yml` - Alert routing config

### Azure Monitor (Optional)

**Purpose:** Export traces and metrics to Azure Application Insights for teams already using Azure.

**Setup:**
- OpenTelemetry SDK instruments FastAPI routes automatically
- Traces and metrics exported to Azure Application Insights / Log Analytics
- Enabled by setting `APPLICATIONINSIGHTS_CONNECTION_STRING` env var
- Disabled when connection string is not set

**Key File:** `backend/app/core/azure_monitor.py`

### CI/CD (GitHub Actions)

**Purpose:** Automated testing and linting on every push.

**Workflow:** `.github/workflows/ci.yml`
- Runs on push to main and PRs
- Lints with Ruff
- Runs pytest test suite
- DB-dependent tests skipped in CI (no database available)


