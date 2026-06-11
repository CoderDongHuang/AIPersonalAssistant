# Personal AI Assistant — Docker Image
# Multi-stage build for a lightweight production image
#
# Build:  docker build -t ai-assistant .
# Run:    docker run -it --env-file .env ai-assistant
# Compose: docker-compose up

FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ── Production stage ──
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Ensure local bin is on PATH
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default timezone
ENV TZ=Asia/Shanghai

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "from config.settings import settings; print(settings.APP_ENV)" || exit 1

# Default: interactive CLI mode
ENTRYPOINT ["python", "main.py"]
CMD []
