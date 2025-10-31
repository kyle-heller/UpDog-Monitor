# UpDog Monitor

> "What's updog?" - "Not much, what's up with you?"

A URL uptime monitoring service that tracks availability and response times, with alerts when things go down.

## Planned Features

- Monitor URLs for uptime
- Track response times and history
- Discord alerts on downtime
- Prometheus metrics
- Web dashboard

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python) |
| Database | PostgreSQL |
| ORM | SQLAlchemy (async) |
| Frontend | React |
| Containers | Docker Compose |

## Setup

```bash
git clone https://github.com/kyle-heller/updog-monitor.git
cd updog-monitor
docker compose up -d db
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload
```

## License

MIT
