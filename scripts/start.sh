#!/bin/bash
# EcoChain Start Script
# Quick start for development

echo "🚀 Starting EcoChain..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please run ./scripts/deploy.sh first."
    exit 1
fi

# Start services
echo "📦 Starting Docker services..."
docker-compose up -d

# Wait a moment
sleep 5

# Check status
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "✅ EcoChain started!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8002"
echo "📚 API Docs: http://localhost:8002/docs"
