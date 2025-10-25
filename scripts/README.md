# 🚀 **EcoChain Scripts**

## **📁 Clean Scripts Directory:**
```
scripts/
├── deploy.sh          # Main deployment script (dev & prod)
├── start.sh           # Quick start for development
├── stop.sh            # Stop all services
└── README.md          # This file
```

## **🔧 Usage:**

### **1. First Time Setup:**
```bash
# Run the deployment script
./scripts/deploy.sh

# Follow the prompts to:
# - Set up environment variables
# - Choose deployment type (dev/prod)
# - Configure your domain (if production)
```

### **2. Daily Development:**
```bash
# Start services
./scripts/start.sh

# Stop services
./scripts/stop.sh
```

### **3. Production Deployment:**
```bash
# Deploy to production
./scripts/deploy.sh
# Choose option 2 (Production)
# Enter your domain
```

## **🎯 What Each Script Does:**

### **`deploy.sh` - Main Deployment Script:**
- ✅ Checks prerequisites (Docker, Docker Compose, Git)
- ✅ Creates .env from template if missing
- ✅ Asks for deployment type (dev/prod)
- ✅ Builds and starts all services
- ✅ Checks service health
- ✅ Shows service URLs and status

### **`start.sh` - Quick Start:**
- ✅ Starts all Docker services
- ✅ Shows service status
- ✅ Displays access URLs

### **`stop.sh` - Stop Services:**
- ✅ Stops all Docker services
- ✅ Cleans up containers

## **🌐 Service URLs (After Start):**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8002
- **API Docs**: http://localhost:8002/docs
- **MeTTa Service**: http://localhost:8007
- **User Agent**: http://localhost:8005
- **Reasoner Agent**: http://localhost:8003
- **Minting Agent**: http://localhost:8004
- **Analytics Agent**: http://localhost:8006

## **🔧 Troubleshooting:**

### **Check Logs:**
```bash
docker-compose logs backend
docker-compose logs frontend
```

### **Restart Services:**
```bash
docker-compose restart
```

### **Rebuild Services:**
```bash
docker-compose build --no-cache
docker-compose up -d
```

---

**🎉 Simple, clean, and works for both development and production!** 🚀🐳✅
