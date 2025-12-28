# Rasa Bot Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Rasa bot files
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYDANTIC_V1=1

# Create non-root user
RUN useradd -m -u 1000 rasauser && \
    chown -R rasauser:rasauser /app
USER rasauser

# Expose Rasa ports
EXPOSE 5005 5055

# Train model on container start if needed
RUN if [ ! -d "models" ] || [ -z "$(ls -A models)" ]; then rasa train; fi

# Default command (can be overridden)
CMD ["rasa", "run", "--port", "5005", "--enable-api", "--cors", "*"]