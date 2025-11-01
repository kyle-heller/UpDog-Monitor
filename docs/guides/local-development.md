# Local Development

## Setup

```bash
# Start database
docker compose up -d db

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Verify
curl http://localhost:8000/api/health
open http://localhost:8000/docs
```

## Common Commands

```bash
# Database
docker compose up -d            # Start
docker compose down             # Stop (keeps data)
docker compose down -v          # Stop and delete data
docker exec -it updog-db psql -U postgres -d updog_dev

# Run API
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload

# Test endpoints
curl http://localhost:8000/api/monitors
curl -X POST http://localhost:8000/api/monitors \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "name": "Example"}'
```
