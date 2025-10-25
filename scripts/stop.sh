#!/bin/bash
# EcoChain Stop Script

echo "🛑 Stopping EcoChain..."

# Stop services
docker-compose down

echo "✅ EcoChain stopped!"
