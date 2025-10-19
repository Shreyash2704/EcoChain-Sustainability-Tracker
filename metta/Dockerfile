# MeTTa Docker Container for Sustainability Analysis
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install only essential dependencies (no MeTTa package)
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    aiohttp \
    pydantic \
    python-multipart

# Create directories
RUN mkdir -p /app/knowledge /app/data /app/api

# Copy MeTTa knowledge base
COPY knowledge/ /app/knowledge/
COPY api/ /app/api/

# Copy main MeTTa script
COPY sustainability.metta /app/
COPY run_metta.py /app/

# Set environment variables
ENV PYTHONPATH=/app
ENV METTA_PORT=8080
ENV METTA_HOST=0.0.0.0

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run MeTTa service
CMD ["python", "run_metta.py"]
