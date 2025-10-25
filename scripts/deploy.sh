#!/bin/bash
# EcoChain Deployment Script
# Works for both development and production

set -e

echo "🚀 EcoChain Deployment Script"
echo "============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please don't run as root. Use a regular user with sudo access."
    exit 1
fi

# Check prerequisites
print_status "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    print_error "Docker not found. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

if ! command -v git &> /dev/null; then
    print_error "Git not found. Please install Git first."
    exit 1
fi

print_success "Prerequisites check passed!"

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from template..."
    if [ -f "env.template" ]; then
        cp env.template .env
        print_success "Created .env from template. Please edit it with your values."
        print_warning "Edit .env file with your API keys and configuration before continuing."
        read -p "Press Enter after updating .env file..."
    else
        print_error "env.template not found. Please create .env file manually."
        exit 1
    fi
fi

# Ask for deployment type
echo ""
echo "Select deployment type:"
echo "1) Development (localhost)"
echo "2) Production (with domain)"
echo "3) Docker only (no domain setup)"
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        print_status "Setting up for development..."
        export ENVIRONMENT=development
        export DEV=true
        ;;
    2)
        print_status "Setting up for production..."
        export ENVIRONMENT=production
        export DEV=false
        
        read -p "Enter your production domain (e.g., https://your-domain.com): " PROD_DOMAIN
        if [ -z "$PROD_DOMAIN" ]; then
            print_error "Production domain is required!"
            exit 1
        fi
        
        # Update .env with production domain
        sed -i "s|PROD_URL=.*|PROD_URL=$PROD_DOMAIN|g" .env
        print_success "Updated .env with production domain: $PROD_DOMAIN"
        ;;
    3)
        print_status "Setting up Docker-only deployment..."
        export ENVIRONMENT=production
        export DEV=false
        ;;
    *)
        print_error "Invalid choice. Exiting."
        exit 1
        ;;
esac

# Build and start services
print_status "Building and starting services..."
docker-compose build
docker-compose up -d

# Wait for services to start
print_status "Waiting for services to start..."
sleep 30

# Check service health
print_status "Checking service health..."

# Check backend
if curl -f http://localhost:8002/health >/dev/null 2>&1; then
    print_success "Backend is healthy"
else
    print_warning "Backend health check failed"
fi

# Check frontend
if curl -f http://localhost:3000 >/dev/null 2>&1; then
    print_success "Frontend is healthy"
else
    print_warning "Frontend health check failed"
fi

# Check agents
print_status "Checking AI agents..."
for agent in user-agent reasoner-agent minting-agent analytics-agent; do
    if docker-compose ps | grep -q "$agent.*Up"; then
        print_success "$agent is running"
    else
        print_warning "$agent is not running"
    fi
done

# Display service status
echo ""
print_status "Service Status:"
docker-compose ps

echo ""
print_success "Deployment completed!"
echo ""
print_status "Service URLs:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8002"
echo "  API Docs: http://localhost:8002/docs"
echo "  MeTTa Service: http://localhost:8007"
echo "  User Agent: http://localhost:8005"
echo "  Reasoner Agent: http://localhost:8003"
echo "  Minting Agent: http://localhost:8004"
echo "  Analytics Agent: http://localhost:8006"
echo ""

if [ "$choice" = "2" ]; then
    print_status "Production deployment notes:"
    echo "  1. Configure your domain to point to this server"
    echo "  2. Set up SSL certificates (Let's Encrypt)"
    echo "  3. Configure firewall (ports 80, 443, 8002)"
    echo "  4. Set up monitoring and backups"
fi

print_success "EcoChain is ready! 🎉"
