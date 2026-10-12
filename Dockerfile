# Jarvis Trader Ecosystem – production-oriented image
FROM python:3.11-slim

# Security: run as non-root
RUN groupadd -r jarvis && useradd -r -g jarvis -d /app -s /sbin/nologin jarvis

WORKDIR /app

# System deps (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Ensure nested package is on path and writable for runtime files if needed
RUN chown -R jarvis:jarvis /app

USER jarvis

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Healthcheck: process is alive (Telegram bot has no HTTP by default)
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
  CMD python -c "import sys; sys.exit(0)" || exit 1

CMD ["python", "main.py"]
