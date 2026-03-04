FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN groupadd -r app && useradd -r -g app app

COPY --chown=app:app . .

# Railway overrides via PORT env var
ENV PORT=8000

EXPOSE $PORT

RUN chmod +x start.sh

USER app

CMD ["./start.sh"]
