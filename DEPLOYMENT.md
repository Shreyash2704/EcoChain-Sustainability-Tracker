# 🚀 **EcoChain Deployment Guide**

## **📁 Clean File Structure:**
```
EcoChain-Sustainability-Tracker/
├── docker-compose.yml          # Single file for dev & prod
├── .env                        # Environment variables
├── backend/
│   ├── Dockerfile             # Backend container
│   └── requirements.txt       # Python dependencies
├── client/
│   ├── Dockerfile             # Frontend container
│   └── package.json           # Node dependencies
└── nginx/
    └── nginx.conf             # Reverse proxy config
```

## **🔧 Development Deployment:**

### **Step 1: Setup Environment**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your values
nano .env
```

### **Step 2: Start Services**
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### **Step 3: Access Services**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8002
- **API Docs**: http://localhost:8002/docs

## **🌐 Production Deployment:**

### **Step 1: Update Environment**
```bash
# Edit .env for production
nano .env

# Set production values:
DEV=false
PROD_URL=https://your-domain.com
ENVIRONMENT=production
```

### **Step 2: Deploy**
```bash
# Deploy to production
ENVIRONMENT=production docker-compose up -d
```

## **📊 Environment Variables:**

### **Development (.env):**
```bash
DEV=true
DEV_URL=http://localhost:8002
PROD_URL=https://api.ecochain.app
ENVIRONMENT=development
```

### **Production (.env):**
```bash
DEV=false
DEV_URL=http://localhost:8002
PROD_URL=https://your-domain.com
ENVIRONMENT=production
```

## **🎯 Key Features:**

### **✅ Single Docker Compose File:**
- Works for both development and production
- Uses environment variables to switch modes
- No duplicate files

### **✅ Smart Environment Detection:**
- `DEV=true` → Development mode
- `DEV=false` → Production mode
- URLs automatically configured

### **✅ Simple Commands:**
```bash
# Development
docker-compose up -d

# Production
ENVIRONMENT=production docker-compose up -d
```

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

### **Stop Services:**
```bash
docker-compose down
```

---

**🎉 Clean, simple, and works for both development and production!** 🚀🐳✅
