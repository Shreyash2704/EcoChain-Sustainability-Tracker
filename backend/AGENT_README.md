# EcoChain Sustainability Tracker Agents

## Overview
EcoChain is a decentralized sustainability tracker that uses AI agents to verify and reward sustainable actions. Our multi-agent system processes sustainability documents, calculates carbon impact, and mints blockchain rewards.

## Agent Architecture

### 1. User Agent (Port 8005)
**Role**: Main orchestrator for all user interactions
**Capabilities**:
- Intent classification using OpenAI
- Request routing to specialized agents
- Chat management and user guidance
- Multi-agent coordination

**Endpoints**:
- `/agents/user/chat` - Chat interface
- `/agents/user/health` - Health check

### 2. Reasoner Agent (Port 8003)
**Role**: Sustainability analysis and carbon impact calculation
**Capabilities**:
- MeTTa-based reasoning for sustainability metrics
- Document analysis and processing
- Carbon footprint calculations
- Environmental impact assessment

**Endpoints**:
- `/agents/reasoner/analyze` - Document analysis
- `/agents/reasoner/health` - Health check

### 3. Minting Agent (Port 8004)
**Role**: Blockchain operations and token management
**Capabilities**:
- ECO token minting (ERC-20)
- SustainabilityProof NFT creation (ERC-721)
- Proof Registry management
- Transaction monitoring

**Endpoints**:
- `/agents/minting/mint` - Token minting
- `/agents/minting/health` - Health check

### 4. Analytics Agent (Port 8006)
**Role**: Data analytics and user insights
**Capabilities**:
- User analytics and statistics
- Leaderboard management
- System overview and metrics
- Blockchain data aggregation

**Endpoints**:
- `/agents/analytics/user/{wallet}` - User analytics
- `/agents/analytics/leaderboard` - Leaderboard data
- `/agents/analytics/health` - Health check

## Technology Stack
- **Framework**: uAgents (Fetch.ai)
- **AI/ML**: OpenAI, MeTTa reasoning
- **Blockchain**: Ethereum Sepolia, Hardhat
- **Storage**: IPFS (Lighthouse)
- **Frontend**: React, TypeScript, TailwindCSS

## Integration
All agents are configured as **Mailbox Agents** for Agentverse integration:
- `mailbox=True` - Enables Agentverse connectivity
- `publish_agent_details=True` - Makes agents discoverable
- Automatic registration on Almanac contract
- Secure communication via Agentverse

## Usage
1. Start the backend server: `python app.py`
2. Agents automatically register on Agentverse
3. Use the Agent Inspector URLs to monitor agent status
4. Agents are discoverable and can communicate with other Agentverse agents

## Demo Features
- **Document Upload**: Upload sustainability documents for analysis
- **Chat Interface**: Natural language interaction with AI agents
- **Dashboard**: Real-time analytics and NFT gallery
- **Blockchain Integration**: Transparent token rewards and NFT proofs
- **Leaderboard**: Community sustainability rankings

## Prize Track Integrations
- **ASI Alliance**: uAgents, Agentverse, MeTTa reasoning
- **Blockscout**: Real-time blockchain data and NFT display
- **Hardhat**: Comprehensive smart contract testing and deployment

For more information, visit: [EcoChain GitHub Repository]
