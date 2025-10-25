# MeTTa Service Dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install build tools
RUN pip install --upgrade pip setuptools wheel

# Copy requirements first for better caching
COPY requirements-simple.txt .

# Install dependencies from requirements file
RUN pip install --no-cache-dir -r requirements-simple.txt

# Copy MeTTa service code
COPY . .

# Create data and knowledge directories
RUN mkdir -p /app/data /app/knowledge

# Create non-root user
RUN useradd -m -u 1000 metta && chown -R metta:metta /app
USER metta

# Expose port
EXPOSE 8007

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8007/health || exit 1

# Start MeTTa service
CMD ["python", "run_metta.py"]