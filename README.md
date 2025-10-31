# UpDog Monitor

> "What's updog?" — "Not much, what's up with you?"

A URL uptime monitoring service that tracks availability and response times, with Discord alerts when things go down.

**Status:** v0.1 (Backend API in development)

## Features

- [ ] Monitor URLs for uptime
- [ ] Track response times
- [ ] View check history
- [ ] Discord alerts on downtime
- [ ] Prometheus metrics
- [ ] Web dashboard

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python) |
| Database | PostgreSQL |
| ORM | SQLAlchemy (async) |
| Frontend | React (coming in v0.2) |
| Containers | Docker Compose |
| Metrics | Prometheus |

## Quick Start

### Prerequisites

- Python 3.12+ (via pyenv)
- Docker & Docker Compose
- Node 22+ (for frontend, later)

### Setup

```bash
# Clone the repo
git clone https://github.com/[username]/updog-monitor.git
cd updog-monitor

# Copy environment file
cp .env.example .env

# Start the database
docker-compose up -d

# Install Python dependencies
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the API
uvicorn app.main:app --reload
```

### Verify It's Working

```bash
# Health check
curl http://localhost:8000/api/health

# API docs
open http://localhost:8000/docs
```

## Project Structure

```
updog-monitor/
├── backend/                # FastAPI application
│   ├── app/
│   │   ├── main.py         # App entry point
│   │   ├── api/            # Route handlers
│   │   ├── models/         # SQLAlchemy models
│   │   ├── core/           # Config, database setup
│   │   └── worker/         # Background check worker
│   └── requirements.txt
├── frontend/               # React app (v0.2+)
├── docs/                   # Documentation
│   ├── PROJECT_CHARTER.md
│   └── architecture/
├── docker-compose.yml
├── .env.example
└── README.md
```

## Documentation

- [Project Charter](docs/PROJECT_CHARTER.md) — Goals, scope, milestones
- [Architecture Overview](docs/architecture/overview.md) — System design
- [Local Development](docs/guides/local-development.md) — Setup guide

## Roadmap

See [PROJECT_CHARTER.md](docs/PROJECT_CHARTER.md) for full milestone breakdown.

| Version | Status | Description |
|---------|--------|-------------|
| 0.1 | 🚧 In Progress | Backend API + worker |
| 0.2 | ⏳ Planned | React frontend |
| 0.3 | ⏳ Planned | History & charts |
| 1.0 | ⏳ Planned | Azure AKS deployment |

## License

MIT
