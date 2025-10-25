# dockerfile backend
# Simple Backend Dockerfile (Uses uvicorn instead of gunicorn)
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install build tools
RUN pip install --upgrade pip setuptools wheel

# Copy requirements first for better caching
COPY requirements.txt .

# Install NumPy first (with specific version to avoid compilation issues)
RUN pip install --no-cache-dir numpy==1.24.3

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Create non-root user
RUN useradd -m -u 1000 ecochain && chown -R ecochain:ecochain /app
USER ecochain

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Start command (using uvicorn instead of gunicorn)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002"]
