#!/bin/sh
# Run database migrations before starting the app
alembic upgrade head

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
