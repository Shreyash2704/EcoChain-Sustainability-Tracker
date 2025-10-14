# EcoChain Backend Setup Guide

## Installation

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Development Dependencies (Optional)**
   ```bash
   pip install -r requirements-dev.txt
   ```

## Environment Configuration

Create a `.env` file in the backend directory with the following variables:

```bash
# Application Configuration
ENVIRONMENT=development
DEBUG=true
APP_NAME=EcoChain Sustainability Tracker
HOST=localhost
PORT=8002

# uAgents Bureau Configuration
BUREAU_PORT=8001

# Blockchain RPC Endpoints
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/YOUR_INFURA_KEY
POLYGON_RPC_URL=https://polygon-mainnet.infura.io/v3/YOUR_INFURA_KEY
ARBITRUM_RPC_URL=https://arbitrum-mainnet.infura.io/v3/YOUR_INFURA_KEY

# API Keys
PRIVY_APP_ID=your_privy_app_id
PRIVY_APP_SECRET=your_privy_app_secret
LIGHTHOUSE_API_KEY=your_lighthouse_api_key
METTA_API_KEY=your_metta_api_key

# Database Configuration (Optional)
DATABASE_URL=postgresql://user:password@localhost:5432/ecochain

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Web3 Configuration
PRIVATE_KEY=your_private_key_here
CONTRACT_ADDRESS=your_contract_address_here

# IPFS Configuration
IPFS_GATEWAY_URL=https://gateway.lighthouse.storage
```

## Running the Application

1. **Start the Backend Server**
   ```bash
   cd backend
   python app.py
   ```

2. **Run Tests**
   ```bash
   python test_upload.py
   ```

3. **Development Mode with Auto-reload**
   ```bash
   uvicorn app:app --reload --host localhost --port 8002
   ```

## API Endpoints

- **Health Check**: `GET /health`
- **File Upload**: `POST /upload/`
- **Upload Status**: `GET /upload/{upload_id}/status`
- **Get CID**: `GET /upload/{upload_id}/cid`
- **Chat with Agent**: `POST /chat`

## Dependencies Overview

### Core Framework
- **FastAPI**: Web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI
- **Pydantic**: Data validation and settings management

### uAgents Framework
- **uagents**: Multi-agent system framework
- **uagents-core**: Core uAgents functionality

### Web3 and Blockchain
- **web3**: Ethereum interaction library
- **eth-account**: Ethereum account management
- **eth-typing**: Type definitions for Ethereum

### HTTP and API
- **requests**: HTTP library for API calls
- **httpx**: Async HTTP client

### Authentication
- **PyJWT**: JSON Web Token handling
- **cryptography**: Cryptographic functions

### File Handling
- **aiofiles**: Async file operations
- **python-multipart**: Multipart form data handling

### Development Tools
- **pytest**: Testing framework
- **black**: Code formatter
- **flake8**: Linting
- **mypy**: Type checking
