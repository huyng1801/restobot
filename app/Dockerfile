# FastAPI Backend Dockerfile
FROM python:3.9-slim

WORKDIR /

# Set Python path for imports (trùng với WORKDIR)
ENV PYTHONPATH=/

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements and install Python dependencies
COPY requirements.txt ./app/
RUN pip install --no-cache-dir -r ./app/requirements.txt

# Copy application code
COPY . ./app/

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

WORKDIR /

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run import tests first, then start FastAPI
CMD python3 -m app.test_imports && uvicorn app.main:app --host 0.0.0.0 --port 8000