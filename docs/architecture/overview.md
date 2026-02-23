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

## How it fits together

The backend is a FastAPI app that does two things: serves a REST API for managing monitors (CRUD, health, SLO reports), and runs a background worker via APScheduler that pings monitored URLs every 60 seconds. Check results go into PostgreSQL, and state changes (up→down or down→up) trigger Discord alerts.

The frontend is a React SPA that talks to the backend API. In docker-compose it goes through an nginx reverse proxy; on Railway the frontend hits the backend URL directly.

Prometheus scrapes the `/metrics` endpoint (basic auth protected) every 15 seconds. Alert rules evaluate SLO thresholds - availability, latency percentiles, error budget burn rate - and Alertmanager routes firing alerts to Discord. Grafana Cloud dashboards visualize everything.

Azure Monitor integration is optional - set the `APPLICATIONINSIGHTS_CONNECTION_STRING` env var and it auto-instruments FastAPI routes via the OpenTelemetry SDK.

## Key file layout

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

frontend/src/
├── pages/
│   ├── Dashboard.tsx
│   ├── MonitorDetail.tsx
│   └── AddMonitor.tsx
└── api/
    └── monitors.ts
```

## CI/CD

GitHub Actions runs on push to main and PRs - lints with Ruff, runs pytest, type-checks the frontend build. On push to main it also builds and pushes Docker images to GHCR. DB-dependent tests are skipped in CI since there's no database available.
