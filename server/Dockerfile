# ── Build stage ──────────────────────────────────────────────────────
FROM python:3.13-slim AS builder

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml .
COPY uv.lock* .

# Install dependencies
RUN uv sync --no-dev --no-install-project

# Copy source code
COPY src/ src/

# Install the project
RUN uv sync --no-dev

# ── Runtime stage ────────────────────────────────────────────────────
FROM python:3.13-slim AS runtime

WORKDIR /app

# Copy installed packages and app from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

# Set path to use virtual environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

EXPOSE 8000

CMD ["uvicorn", "server.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
