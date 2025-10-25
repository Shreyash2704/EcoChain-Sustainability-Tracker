#!/bin/bash
# Rebuild backend container with new Dockerfile

echo "🔧 Rebuilding Backend Container with Fixed Dockerfile"
echo "====================================================="

# Stop all services
echo "🛑 Stopping all services..."
docker-compose -f docker-compose.optimized.yml down

# Remove old backend image
echo "🗑️ Removing old backend image..."
docker rmi ecochain-sustainability-tracker-backend 2>/dev/null || true

# Rebuild backend with no cache
echo "📦 Rebuilding backend container..."
docker-compose -f docker-compose.optimized.yml build --no-cache backend

# Start services
echo "🚀 Starting services..."
docker-compose -f docker-compose.optimized.yml up -d

# Check status
echo "📊 Checking service status..."
docker-compose -f docker-compose.optimized.yml ps

echo ""
echo "✅ Backend rebuild completed!"
echo ""
echo "🌐 Service URLs:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8002"
echo "  API Docs: http://localhost:8002/docs"
