# Use official Python image as base
FROM python:3.12-slim

WORKDIR /app

# Copy requirements first (Docker layer caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Default port (Railway overrides via PORT env var)
ENV PORT=8000

# Expose the port
EXPOSE $PORT

# Make start script executable and run it
RUN chmod +x start.sh
CMD ["./start.sh"]
