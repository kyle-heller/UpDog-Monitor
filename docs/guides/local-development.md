# Local Development Guide

## Prerequisites

Before starting, ensure you have:

- [ ] Python 3.12+ (via pyenv)
- [ ] Docker Desktop running
- [ ] Git configured

Verify with:

```bash
python --version    # Should show 3.12.x
docker --version    # Should show Docker version
git --version       # Should show git version
```

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/[username]/updog-monitor.git
cd updog-monitor
```

### 2. Set Python Version

```bash
# Set project-specific Python version
pyenv local 3.12.10

# Verify
python --version
```

### 3. Create Environment File

```bash
# Copy the template
cp .env.example .env

# Edit if needed (defaults work for local dev)
```

### 4. Start the Database

```bash
# Start PostgreSQL in Docker
docker-compose up -d

# Verify it's running
docker-compose ps

# Check logs if needed
docker-compose logs db
```

### 5. Set Up Python Environment

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 6. Run the API

```bash
# From backend/ directory with venv activated
uvicorn app.main:app --reload

# You should see:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Started reloader process
```

### 7. Verify It's Working

```bash
# Health check
curl http://localhost:8000/api/health

# Open API docs
open http://localhost:8000/docs
```

## Daily Development Workflow

### Starting Your Day

```bash
cd updog-monitor

# Start database (if not running)
docker-compose up -d

# Activate Python environment
cd backend
source .venv/bin/activate

# Run the API
uvicorn app.main:app --reload
```

### Making Changes

1. Edit code in `backend/app/`
2. Uvicorn auto-reloads on save
3. Test your changes
4. Commit when something works

### Ending Your Day

```bash
# Stop the API: Ctrl+C

# Optional: Stop the database
docker-compose down

# Or leave it running (uses minimal resources)
```

## Common Commands

### Database

```bash
# Start
docker-compose up -d

# Stop (keeps data)
docker-compose down

# Stop and delete data
docker-compose down -v

# View logs
docker-compose logs -f db

# Connect with psql
docker exec -it updog-db psql -U postgres -d updog_dev
```

### Python

```bash
# Activate venv
source .venv/bin/activate

# Deactivate venv
deactivate

# Install new package
pip install package-name
pip freeze > requirements.txt

# Run API
uvicorn app.main:app --reload

# Run with different port
uvicorn app.main:app --reload --port 8001
```

### Testing API

```bash
# Health check
curl http://localhost:8000/api/health

# List monitors
curl http://localhost:8000/api/monitors

# Create monitor
curl -X POST http://localhost:8000/api/monitors \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "name": "Example"}'

# Get monitor
curl http://localhost:8000/api/monitors/{id}

# Delete monitor
curl -X DELETE http://localhost:8000/api/monitors/{id}
```

## Troubleshooting

### Database won't start

```bash
# Check if port 5432 is in use
lsof -i :5432

# Kill whatever's using it, or change the port in docker-compose.yml
```

### "Module not found" errors

```bash
# Make sure venv is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Changes not reflecting

```bash
# Make sure you're editing the right files
# Uvicorn should show "Detected change, reloading..."

# If not, restart manually
# Ctrl+C then run uvicorn again
```

### Can't connect to database

```bash
# Check if database is running
docker-compose ps

# Check database logs
docker-compose logs db

# Verify connection string in .env matches docker-compose.yml
```

## Project Structure

```
updog-monitor/
├── backend/
│   ├── .venv/              # Python virtual environment (gitignored)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # FastAPI app entry point
│   │   ├── api/            # Route handlers
│   │   ├── models/         # SQLAlchemy models
│   │   ├── core/           # Config, database
│   │   └── worker/         # Background checker
│   └── requirements.txt
├── frontend/               # React app (v0.2+)
├── docs/
├── docker-compose.yml
├── .env                    # Your local config (gitignored)
├── .env.example            # Template (committed)
├── .gitignore
└── README.md
```
