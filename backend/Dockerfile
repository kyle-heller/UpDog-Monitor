# Use official Python image as base
# "slim" variant is smaller (no extra tools we don't need)
FROM python:3.12-slim

# Set working directory inside the container
# All subsequent commands run from here
WORKDIR /app

# Copy requirements first (before code)
# Why? Docker caches layers. If requirements.txt hasn't changed,
# Docker reuses the cached "pip install" layer = faster builds
COPY requirements.txt .

# Install dependencies
# --no-cache-dir: Don't store pip's cache (smaller image)
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the application code
COPY . .

# Expose port 8000 (documentation for humans, doesn't actually open it)
EXPOSE 8000

# Command to run when container starts
# "0.0.0.0" = listen on all interfaces (required in Docker)
# If you use "127.0.0.1", other containers can't reach it
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
