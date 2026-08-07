# =====================================================================
# PRASHANTH HOSPITALS — FASTAPI BACKEND MULTI-STAGE DOCKERFILE
# =====================================================================

# ---------------------------------------------------------------------
# STAGE 1: Builder Stage (Compiles wheel dependencies)
# ---------------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /build

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment for clean dependency isolation
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python requirements
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------
# STAGE 2: Production Runtime Stage (Minimal size, non-root user)
# ---------------------------------------------------------------------
FROM python:3.11-slim AS runner

WORKDIR /app

# Install runtime system libraries (libpq for PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-built virtualenv from builder stage
COPY --from=builder /opt/venv /opt/venv

# Configure environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_ENV=production \
    PORT=8000

# Create non-root system user for container security
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser

# Copy application source code
COPY backend/app /app/backend/app
COPY backend/requirements.txt /app/backend/requirements.txt

# Set file ownership to non-root user
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

# Health check to ensure Uvicorn backend process is responding
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start multi-worker Uvicorn production server
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
