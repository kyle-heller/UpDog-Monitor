# UpDog Monitor

> "What's updog?" — "Not much, what's up with you?"

A URL uptime monitoring service with Prometheus metrics, Discord alerts, and SLO tracking.

## Features

- Monitor URLs for uptime and response time
- Prometheus metrics endpoint (`/metrics`)
- Grafana dashboard with pre-built panels
- Discord alerts on state changes (DOWN/RECOVERED)
- SLO tracking with error budgets
- Operational runbooks

## Quick Start

```bash
# Start everything
docker compose up --build

# Or for development (run API locally)
docker compose up -d db prometheus grafana
cd backend && uvicorn app.main:app --reload
```

**URLs:**
- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python 3.12) |
| Frontend | React + Vite |
| Database | PostgreSQL |
| Metrics | Prometheus + Grafana |
| Alerts | Discord webhooks |

## Project Structure

```
updog-monitor/
├── backend/
│   ├── app/
│   │   ├── api/           # Route handlers
│   │   ├── core/          # Config, db, metrics, SLO
│   │   ├── models/        # SQLAlchemy models
│   │   └── worker/        # Background checker
│   └── Dockerfile
├── frontend/
│   ├── src/
│   └── Dockerfile
├── docs/
│   └── runbooks/          # Operational playbooks
├── grafana/               # Dashboard provisioning
├── docker-compose.yml
└── prometheus.yml
```

## Configuration

Set via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | localhost |
| `DISCORD_WEBHOOK_URL` | Discord webhook for alerts | (disabled) |

## Documentation

- [Runbooks](docs/runbooks/) — Incident response guides
- [Architecture](docs/architecture/) — System design

## License

MIT
